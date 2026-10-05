"""Run a historical generation pipeline from the terminal or a CI job."""

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from urllib.error import URLError

import duckdb

from electricity_pipeline.source import archive, fetch, monthly_windows
from electricity_pipeline.validation import MADRID, parse
from electricity_pipeline.warehouse import connect, export_csv, load, quality


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--start", required=True, type=date.fromisoformat, help="YYYY-MM-DD inclusive"
    )
    parser.add_argument(
        "--end", required=True, type=date.fromisoformat, help="YYYY-MM-DD inclusive"
    )
    parser.add_argument("--database", type=Path, default=Path("data/electricity.duckdb"))
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--export-dir", type=Path, default=Path("data/exports"))
    args = parser.parse_args(argv)
    if args.end >= datetime.now(MADRID).date():
        parser.error("Use closed historical dates; today and future dates are not supported")
    if args.start > args.end:
        parser.error("--start must be on or before --end")
    try:
        with connect(args.database) as connection:
            for window in monthly_windows(args.start, args.end):
                print(f"Fetching {window.start} through {window.end} (peninsular)", flush=True)
                body = fetch(window)
                retrieval = archive(body, window, args.raw_dir)
                batch = parse(body, window)
                load(connection, batch, retrieval)
                print(
                    json.dumps(
                        {
                            "loaded_observations": len(batch.observations),
                            "source_sha256": retrieval.sha256,
                            "source_updated_at": batch.source_updated_at,
                        }
                    ),
                    flush=True,
                )
            checks = quality(connection)
            paths = export_csv(connection, args.export_dir)
            print(f"All {len(checks)} SQL quality checks passed")
            for path in paths:
                print(f"Exported {path}")
    except (ValueError, OSError, URLError, duckdb.Error) as error:
        print(f"Pipeline failed: {error}", file=sys.stderr)
        return 1
    return 0
