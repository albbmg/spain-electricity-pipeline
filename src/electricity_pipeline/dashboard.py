"""Build a portable, offline dashboard from validated complete historical years."""

import argparse
import json
import os
import sys
import tempfile
from datetime import date
from importlib.resources import files
from pathlib import Path

import duckdb

from electricity_pipeline.history import periods
from electricity_pipeline.source import REGION


def snapshot(connection: duckdb.DuckDBPyConnection, start_year: int, end_year: int) -> dict:
    """Compute display values in Decimal, preserving the history completeness gate."""
    months = [p for p in periods(connection, start_year, end_year) if p.grain == "month"]
    indexed = {p.start: p for p in months}
    monthly_evidence = {p.start: [] for p in months}
    for month, *record in connection.execute(
        "SELECT DISTINCT CAST(date_trunc('month', t.day) AS DATE) AS month, "
        "r.retrieval_id, r.start_date, r.end_date, "
        "r.source_updated_at, r.retrieved_at, r.sha256 "
        "FROM ingestion_runs r JOIN source_totals t USING (retrieval_id) "
        "WHERE t.region = ? AND t.day BETWEEN ? AND ? "
        "ORDER BY month, r.start_date, r.retrieved_at, r.retrieval_id",
        [REGION, months[0].start, date(end_year, 12, 31)],
    ).fetchall():
        monthly_evidence[month].append([str(value) for value in record])
    comparisons = {}
    for current in months:
        previous = (
            indexed.get(date(current.start.year - 1, current.start.month, 1))
            if current.start.year > start_year
            else None
        )
        comparisons[current.start] = (
            {
                "previous_month": previous.start.strftime("%Y-%m"),
                "previous_days": previous.days,
                "previous_generation_gwh": f"{previous.generation_mwh / 1000:,.3f}",
                "previous_daily_gwh": f"{previous.daily_mwh / 1000:,.3f}",
                "previous_renewable_share": f"{previous.share:.2%}",
                "generation_yoy": (f"{current.generation_mwh / previous.generation_mwh - 1:+.2%}"),
                "daily_yoy": f"{current.daily_mwh / previous.daily_mwh - 1:+.2%}",
                "share_change_pp": f"{(current.share - previous.share) * 100:+.2f}",
                "previous_evidence": monthly_evidence[previous.start],
                "current_evidence": monthly_evidence[current.start],
            }
            if previous is not None
            else None
        )
    technology_rows = connection.execute(
        "SELECT month, technology_id, technology, renewable, days_observed, generation_mwh "
        "FROM monthly_technology WHERE region = ? AND month BETWEEN ? AND ? "
        "ORDER BY month, generation_mwh DESC, technology_id, technology, renewable",
        [REGION, months[0].start, months[-1].start],
    ).fetchall()
    totals = {p.start: p.generation_mwh for p in months}
    technologies = {p.start: [] for p in months}
    for month, identity, name, renewable, observed, energy in technology_rows:
        technologies[month].append(
            {
                "id": identity,
                "name": name,
                "renewable": renewable,
                "days_observed": observed,
                "generation_mwh": str(energy),
                "generation_gwh": f"{energy / 1000:,.3f}",
                "system_share": f"{energy / totals[month]:.2%}",
            }
        )
    selections = {}
    for key in ["all", *map(str, range(start_year, end_year + 1))]:
        selected = [p for p in months if key == "all" or p.start.year == int(key)]
        first = selected[0].start
        last = date(selected[-1].start.year, 12, 31)
        energy = sum(p.generation_mwh for p in selected)
        renewable = sum(p.renewable_mwh for p in selected)
        days = sum(p.days for p in selected)
        published, max_difference = connection.execute(
            "SELECT SUM(source_total_mwh), MAX(ABS(reconciliation_difference_mwh)) "
            "FROM daily_mix WHERE region = ? AND day BETWEEN ? AND ?",
            [REGION, first, last],
        ).fetchone()
        evidence = connection.execute(
            "SELECT DISTINCT r.retrieval_id, r.start_date, r.end_date, "
            "r.source_updated_at, r.retrieved_at, r.sha256 "
            "FROM ingestion_runs r JOIN source_totals t USING (retrieval_id) "
            "WHERE t.region = ? AND t.day BETWEEN ? AND ? "
            "ORDER BY r.start_date, r.retrieved_at, r.retrieval_id",
            [REGION, first, last],
        ).fetchall()
        selections[key] = {
            "label": f"{start_year}–{end_year}" if key == "all" else key,
            "days": days,
            "months": len(selected),
            "generation_gwh": f"{energy / 1000:,.3f}",
            "renewable_share": f"{renewable / energy:.2%}",
            "daily_gwh": f"{energy / days / 1000:,.3f}",
            "published_gwh": f"{published / 1000:,.3f}",
            "max_daily_difference_mwh": f"{max_difference:,.6f}",
            "evidence": [[str(value) for value in row] for row in evidence],
            "rows": [
                {
                    "month": p.start.strftime("%Y-%m"),
                    "days": p.days,
                    "daily_gwh": f"{p.daily_mwh / 1000:,.3f}",
                    "generation_gwh": f"{p.generation_mwh / 1000:,.3f}",
                    "renewable_share": f"{p.share:.2%}",
                    # Exact values cross the JSON boundary as decimal strings.
                    # Browser floats are used only for bar widths, never KPI arithmetic.
                    "generation_mwh": str(p.generation_mwh),
                    "renewable_mwh": str(p.renewable_mwh),
                    "technologies": technologies[p.start],
                    "comparison": comparisons[p.start],
                }
                for p in selected
            ],
        }
    return {"default": str(end_year), "selections": selections}


def render(connection: duckdb.DuckDBPyConnection, start_year: int, end_year: int) -> str:
    data = json.dumps(snapshot(connection, start_year, end_year), ensure_ascii=True)
    # Prevent even a source-controlled string from terminating the JSON script element.
    data = data.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    template = files("electricity_pipeline").joinpath("templates/dashboard.html").read_text("utf-8")
    return template.replace("__DASHBOARD_DATA__", data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--start-year", type=int, required=True)
    parser.add_argument("--end-year", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    temporary = None
    try:
        if args.output.suffix.lower() != ".html":
            raise ValueError("Output must be an .html file")
        if args.output.resolve() == args.database.resolve():
            raise ValueError("Output must not overwrite the database")
        with duckdb.connect(str(args.database), read_only=True) as connection:
            document = render(connection, args.start_year, args.end_year)
        # A validation or write failure leaves the previous dashboard intact.
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=args.output.parent, delete=False
        ) as target:
            temporary = Path(target.name)
            target.write(document)
        os.replace(temporary, args.output)
    except (OSError, ValueError, duckdb.Error) as exc:
        print(f"Dashboard failed: {exc}", file=sys.stderr)
        return 1
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
