"""Run a historical generation pipeline from the terminal or a CI job."""

import argparse
import json
import sys
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path
from urllib.error import URLError

import duckdb

from electricity_pipeline.replay import read_manifest
from electricity_pipeline.source import archive, fetch, monthly_windows
from electricity_pipeline.validation import MADRID, parse
from electricity_pipeline.warehouse import connect, export_csv, load, quality


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=date.fromisoformat, help="YYYY-MM-DD inclusive (live mode)")
    parser.add_argument("--end", type=date.fromisoformat, help="YYYY-MM-DD inclusive (live mode)")
    parser.add_argument(
        "--replay-manifest", type=Path, help="Replay one archived retrieval offline"
    )
    parser.add_argument("--database", type=Path, default=Path("data/electricity.duckdb"))
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--export-dir", type=Path, default=Path("data/exports"))
    args = parser.parse_args(argv)
    if args.replay_manifest is not None:
        if args.start is not None or args.end is not None:
            parser.error("--replay-manifest cannot be combined with --start or --end")
    else:
        if args.start is None or args.end is None:
            parser.error("Provide both --start and --end, or use --replay-manifest")
        if args.end >= datetime.now(MADRID).date():
            parser.error("Use closed historical dates; today and future dates are not supported")
        if args.start > args.end:
            parser.error("--start must be on or before --end")
    try:
        # Validate the archive before creating or opening the target warehouse.
        archived = read_manifest(args.replay_manifest) if args.replay_manifest is not None else None
        windows = [] if archived is not None else monthly_windows(args.start, args.end)
        with connect(args.database) as connection:
            if archived is not None:
                batch, retrieval = archived
                revision = load(connection, batch, retrieval, replay=True)
                print(
                    f"Replayed {len(batch.observations)} observations from {retrieval.retrieval_id}"
                )
                print(json.dumps({"revision": asdict(revision)}), flush=True)
            for window in windows:
                print(f"Fetching {window.start} through {window.end} (peninsular)", flush=True)
                body = fetch(window)
                retrieval = archive(body, window, args.raw_dir)
                batch = parse(body, window)
                revision = load(connection, batch, retrieval)
                print(
                    json.dumps(
                        {
                            "loaded_observations": len(batch.observations),
                            "source_sha256": retrieval.sha256,
                            "source_updated_at": batch.source_updated_at,
                            "revision": asdict(revision),
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
