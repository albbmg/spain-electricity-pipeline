"""Transactional date-window replacement and versioned analytical SQL."""

import csv
import uuid
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path

import duckdb

from electricity_pipeline.source import REGION, Retrieval
from electricity_pipeline.validation import Batch


def sql(name: str) -> str:
    return files("electricity_pipeline").joinpath("sql", name).read_text(encoding="utf-8")


def connect(path: Path) -> duckdb.DuckDBPyConnection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(path))
    connection.execute("SET TimeZone = 'UTC'")
    connection.execute(sql("schema.sql"))
    connection.execute(sql("marts.sql"))
    return connection


def quality(connection: duckdb.DuckDBPyConnection) -> list[tuple[str, int]]:
    results = connection.execute(sql("quality.sql")).fetchall()
    failed = [(name, count) for name, count in results if count]
    if failed:
        raise ValueError(f"Warehouse quality checks failed: {failed}")
    return results


def load(
    connection: duckdb.DuckDBPyConnection,
    batch: Batch,
    retrieval: Retrieval,
    *,
    replay: bool = False,
) -> None:
    """Replace a validated partition; any write or quality failure rolls it back."""
    if (retrieval.start_date, retrieval.end_date, retrieval.region) != (
        str(batch.window.start),
        str(batch.window.end),
        REGION,
    ):
        raise ValueError("Retrieval metadata does not match the validated batch")
    bounds = [REGION, batch.window.start, batch.window.end]
    connection.execute("BEGIN TRANSACTION")
    try:
        connection.execute(
            "DELETE FROM generation WHERE region = ? AND day BETWEEN ? AND ?", bounds
        )
        connection.execute(
            "DELETE FROM source_totals WHERE region = ? AND day BETWEEN ? AND ?", bounds
        )
        retrieval_values = [
            retrieval.retrieval_id,
            retrieval.url,
            REGION,
            batch.window.start,
            batch.window.end,
            retrieval.retrieved_at,
            batch.source_updated_at,
            retrieval.sha256,
            retrieval.raw_file,
            len(batch.observations),
        ]
        insert = "INSERT INTO ingestion_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        if replay:
            connection.execute(insert + " ON CONFLICT DO NOTHING", retrieval_values)
            matches = connection.execute(
                "SELECT source_url = ? AND region = ? AND start_date = ? AND end_date = ? "
                "AND retrieved_at = ? AND source_updated_at = ? AND sha256 = ? "
                "AND raw_file = ? AND observation_count = ? "
                "FROM ingestion_runs WHERE retrieval_id = ?",
                retrieval_values[1:] + retrieval_values[:1],
            ).fetchone()
            if matches != (True,):
                raise ValueError("Replay metadata conflicts with the recorded retrieval")
        else:
            connection.execute(insert, retrieval_values)
        connection.executemany(
            "INSERT INTO generation VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    REGION,
                    row.day,
                    row.technology_id,
                    row.technology,
                    row.renewable,
                    row.energy_mwh,
                    float(row.source_share) if row.source_share is not None else None,
                    row.source_updated_at,
                    retrieval.retrieval_id,
                )
                for row in batch.observations
            ],
        )
        connection.executemany(
            "INSERT INTO source_totals VALUES (?, ?, ?, ?)",
            [(REGION, day, energy, retrieval.retrieval_id) for day, energy in batch.totals.items()],
        )
        quality(connection)
        if replay:
            connection.execute(
                "INSERT INTO replay_runs VALUES (?, ?, ?)",
                [uuid.uuid4().hex, retrieval.retrieval_id, datetime.now(UTC)],
            )
        connection.execute("COMMIT")
    except Exception:
        connection.execute("ROLLBACK")
        raise


def export_csv(connection: duckdb.DuckDBPyConnection, directory: Path) -> list[Path]:
    """Write UTF-8 CSVs from verified marts; failed pipelines do not export."""
    quality(connection)
    directory.mkdir(parents=True, exist_ok=True)
    exports = {
        "daily_mix": "region, day",
        "monthly_mix": "region, month",
        "monthly_technology": "region, month, technology_id, technology, renewable",
    }
    paths = []
    for view, order in exports.items():
        # Both identifiers are fixed above, never sourced from CLI input.
        cursor = connection.execute(f"SELECT * FROM {view} ORDER BY {order}")
        path = directory / f"{view}.csv"
        temporary = path.with_suffix(".csv.tmp")
        with temporary.open("w", encoding="utf-8", newline="") as target:
            writer = csv.writer(target)
            writer.writerow([column[0] for column in cursor.description])
            writer.writerows(cursor.fetchall())
        temporary.replace(path)
        paths.append(path)
    return paths
