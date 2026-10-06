"""Report complete historical years with comparable calendar periods and provenance."""

import argparse
import sys
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import duckdb

from electricity_pipeline.source import REGION
from electricity_pipeline.validation import MADRID
from electricity_pipeline.warehouse import quality, sql


@dataclass(frozen=True)
class Period:
    grain: str
    start: date
    days: int
    expected_days: int
    generation_mwh: Decimal
    renewable_mwh: Decimal

    @property
    def share(self) -> Decimal:
        return self.renewable_mwh / self.generation_mwh

    @property
    def daily_mwh(self) -> Decimal:
        return self.generation_mwh / self.days


def periods(connection: duckdb.DuckDBPyConnection, start_year: int, end_year: int) -> list[Period]:
    """Reject missing years, months and days before presenting any comparisons."""
    if not 1 <= start_year < end_year < datetime.now(MADRID).year:
        raise ValueError("Select at least two complete past calendar years in ascending order")
    quality(connection)
    rows = connection.execute(
        sql("historical.sql"),
        [REGION, date(start_year, 1, 1), date(end_year, 12, 31)],
    ).fetchall()
    result = [Period(*row) for row in rows]
    expected_months = {
        date(year, month, 1) for year in range(start_year, end_year + 1) for month in range(1, 13)
    }
    present_months = {period.start for period in result if period.grain == "month"}
    if present_months != expected_months or any(p.days != p.expected_days for p in result):
        raise ValueError("Historical analysis requires every day of every selected calendar year")
    return result


def render(connection: duckdb.DuckDBPyConnection, start_year: int, end_year: int) -> str:
    """Build the entire report only after completeness and warehouse checks pass."""
    values = periods(connection, start_year, end_year)
    years = [period for period in values if period.grain == "year"]
    months = [period for period in values if period.grain == "month"]
    quarters = [period for period in values if period.grain == "quarter"]
    first, last = date(start_year, 1, 1), date(end_year, 12, 31)
    count, technologies = connection.execute(
        "SELECT COUNT(*), COUNT(DISTINCT technology_id) FROM generation "
        "WHERE region = ? AND day BETWEEN ? AND ?",
        [REGION, first, last],
    ).fetchone()
    lines = [
        f"# Peninsular generation: {start_year}–{end_year}",
        "",
        "Source: **Red Eléctrica de España, REData**. Geography: **peninsular Spain**.",
        "",
        f"Coverage: **{sum(p.days for p in years):,} days**, **{len(months)} complete months**, "
        f"**{count:,} technology observations**, **{technologies} source technology IDs**. "
        "All warehouse SQL quality checks passed; every selected calendar date is present.",
        "",
        "## Annual comparison",
        "",
        "Shares are energy-weighted. YoY compares each year with the previous calendar year; "
        "pp means percentage points. Daily averages account for different calendar lengths, "
        "including leap years. They do not adjust for weather or other drivers.",
        "",
        "| Year | Days | Generation (GWh) | GWh/day | Renewable share | Generation YoY | "
        "GWh/day YoY | Share change (pp) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    previous = None
    for current in years:
        energy_change = daily_change = share_change = "—"
        if previous is not None:
            energy_change = f"{current.generation_mwh / previous.generation_mwh - 1:+.2%}"
            daily_change = f"{current.daily_mwh / previous.daily_mwh - 1:+.2%}"
            share_change = f"{(current.share - previous.share) * 100:+.2f}"
        lines.append(
            f"| {current.start.year} | {current.days} | {current.generation_mwh / 1000:,.3f} "
            f"| {current.daily_mwh / 1000:,.3f} | {current.share:.2%} | {energy_change} "
            f"| {daily_change} | {share_change} |"
        )
        previous = current
    lines += [
        "",
        "## Calendar-quarter pattern",
        "",
        "Compare the same quarter across years. Q1–Q4 are calendar quarters, not "
        "meteorological seasons; Q1 includes the extra February day in leap years.",
        "",
        "| Quarter | Days | Generation (GWh) | GWh/day | Renewable share |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for period in quarters:
        lines.append(
            f"| {period.start.year}-Q{(period.start.month - 1) // 3 + 1} | {period.days} "
            f"| {period.generation_mwh / 1000:,.3f} | {period.daily_mwh / 1000:,.3f} "
            f"| {period.share:.2%} |"
        )
    lines += ["", "## Observed within-year range", ""]
    for annual in years:
        candidates = [p for p in months if p.start.year == annual.start.year]
        low = min(candidates, key=lambda p: p.share)
        high = max(candidates, key=lambda p: p.share)
        lines.append(
            f"- {annual.start.year}: monthly renewable share ranged from **{low.share:.2%}** "
            f"({low.start:%Y-%m}) to **{high.share:.2%}** ({high.start:%Y-%m}), "
            f"a **{(high.share - low.share) * 100:.2f} pp** span."
        )
    lines += [
        "",
        "These describe the selected years, not an established long-term seasonal law. "
        "Tied extrema use the earliest month. The table below compares like calendar months.",
        "",
        "## Monthly year-on-year comparison",
        "",
        "| Month | Days | Generation (GWh) | GWh/day | Renewable share | "
        "Generation YoY | GWh/day YoY | Share change (pp) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    indexed = {p.start: p for p in months}
    for current in months:
        previous = (
            indexed.get(date(current.start.year - 1, current.start.month, 1))
            if current.start.year > start_year
            else None
        )
        energy_change = daily_change = share_change = "—"
        if previous is not None:
            energy_change = f"{current.generation_mwh / previous.generation_mwh - 1:+.2%}"
            daily_change = f"{current.daily_mwh / previous.daily_mwh - 1:+.2%}"
            share_change = f"{(current.share - previous.share) * 100:+.2f}"
        lines.append(
            f"| {current.start:%Y-%m} | {current.days} | {current.generation_mwh / 1000:,.3f} "
            f"| {current.daily_mwh / 1000:,.3f} | {current.share:.2%} | {energy_change} "
            f"| {daily_change} | {share_change} |"
        )
    lines += [
        "",
        "## Source evidence",
        "",
        "Only retrievals currently referenced by the selected observations are listed. "
        "Acquisition times and hashes identify this snapshot; replay does not change them.",
        "",
    ]
    evidence = connection.execute(
        "SELECT DISTINCT r.retrieval_id, r.start_date, r.end_date, r.source_updated_at, "
        "r.retrieved_at, r.sha256, r.source_url FROM ingestion_runs r "
        "JOIN source_totals t USING (retrieval_id) "
        "WHERE t.region = ? AND t.day BETWEEN ? AND ? "
        "ORDER BY r.start_date, r.retrieved_at, r.retrieval_id",
        [REGION, first, last],
    ).fetchall()
    for identity, start, end, updated, retrieved, sha, url in evidence:
        lines += [
            f"- Window: {start}–{end}",
            f"  - Retrieval: `{identity}`",
            f"  - Provider last update: {updated.isoformat()}",
            f"  - Retrieved at: {retrieved.isoformat()}",
            f"  - SHA-256: `{sha}`",
            f"  - [Source request]({url})",
        ]
    lines += [
        "",
        "## Interpretation and reproduction",
        "",
        "Generation is not demand, prices or emissions. Renewable classification follows "
        "the source. Published totals remain separate reconciliation controls. These "
        "descriptive comparisons do not establish causes; source revisions may change "
        "the results. No incomplete months or years are included or imputed.",
        "",
        "Run from the repository root:",
        "",
        "```bash",
        f"python -m electricity_pipeline --start {first} --end {last} "
        "--database data/history.duckdb --raw-dir data/history-raw "
        "--export-dir data/history-exports",
        "python -m electricity_pipeline.history --database data/history.duckdb "
        f"--start-year {start_year} --end-year {end_year}",
        "```",
        "",
        "A new API retrieval may contain revisions. To reproduce this exact snapshot, "
        "replay the original manifests and payloads into a separate database, then run "
        "the history command against it. Raw downloads and databases are not committed.",
        "",
        "Independent educational analysis. Source data remain subject to "
        "[Red Eléctrica's terms](https://www.ree.es/es/aviso-legal), not the code's MIT license. "
        "See the [source contract](../docs/source-contract.md).",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=Path("data/history.duckdb"))
    parser.add_argument("--start-year", type=int, required=True)
    parser.add_argument("--end-year", type=int, required=True)
    args = parser.parse_args(argv)
    try:
        with duckdb.connect(str(args.database), read_only=True) as connection:
            connection.execute("SET TimeZone = 'UTC'")
            report = render(connection, args.start_year, args.end_year)
        print(report, end="")
    except (ValueError, OSError, duckdb.Error) as error:
        print(f"Historical report failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
