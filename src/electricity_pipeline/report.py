"""Print an attributed, reproducible baseline from the current warehouse."""

import argparse
from pathlib import Path

import duckdb

from electricity_pipeline.warehouse import quality


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=Path("data/electricity.duckdb"))
    args = parser.parse_args()
    with duckdb.connect(str(args.database), read_only=True) as connection:
        connection.execute("SET TimeZone = 'UTC'")
        checks = quality(connection)
        first, last, days, generation, renewable = connection.execute(
            "SELECT MIN(day), MAX(day), COUNT(*), SUM(generation_mwh), SUM(renewable_mwh) "
            "FROM daily_mix"
        ).fetchone()
        if not days:
            raise ValueError("No validated observations to report")
        rows, technologies = connection.execute(
            "SELECT COUNT(*), COUNT(DISTINCT technology_id) FROM generation"
        ).fetchone()
        print("# Validated baseline\n")
        print("Source: **Red Eléctrica de España, REData**. Geography: **peninsular Spain**.\n")
        print(
            f"Period: **{first}–{last}**. **{days} observed days**, "
            f"**{rows:,} technology observations**, **{technologies} technologies**.\n"
        )
        print(
            f"Generation: **{generation / 1000:,.3f} GWh**. "
            f"Energy-weighted renewable share: **{renewable / generation:.2%}**.\n"
        )
        print("| Month | Days | Complete month | Generation (GWh) | Renewable share |")
        print("| --- | ---: | :---: | ---: | ---: |")
        for month, observed, complete, energy, share in connection.execute(
            "SELECT month, days_observed, is_complete_month, generation_mwh, renewable_share "
            "FROM monthly_mix ORDER BY month"
        ).fetchall():
            print(
                f"| {month:%Y-%m} | {observed} | {'Yes' if complete else 'No'} "
                f"| {energy / 1000:,.3f} | {share:.2%} |"
            )
        print(f"\nAll **{len(checks)} SQL quality checks** passed.\n")
        print("## Source evidence\n")
        print("Only retrievals currently referenced by analytical observations are listed.\n")
        for start, end, updated, retrieved, sha, url in connection.execute(
            "SELECT r.start_date, r.end_date, r.source_updated_at, r.retrieved_at, r.sha256, "
            "r.source_url FROM ingestion_runs r WHERE EXISTS "
            "(SELECT 1 FROM source_totals t WHERE t.retrieval_id = r.retrieval_id) "
            "ORDER BY r.start_date, r.retrieved_at"
        ).fetchall():
            print(
                f"- Window: {start}–{end}\n"
                f"  - Provider last update: {updated.isoformat()}\n"
                f"  - Retrieved at: {retrieved.isoformat()}\n"
                f"  - SHA-256: `{sha}`\n"
                f"  - [Source request]({url})"
            )
        print("\n## Interpretation limits\n")
        print(
            "These are historical generation observations, not demand, prices or emissions. "
            "Renewable status follows the provider's classification. The API's total is "
            "excluded from technology sums and used only for reconciliation. Source data "
            "may be revised; a later retrieval can legitimately change this baseline. "
            "No causal or year-on-year conclusions follow from this initial snapshot.\n"
        )
        print(
            "Reproduce with `python -m electricity_pipeline.report`. "
            "See [the source contract](../docs/source-contract.md) and "
            "[provider terms](https://www.ree.es/es/aviso-legal)."
        )


if __name__ == "__main__":
    main()
