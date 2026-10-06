"""Compare stored values within a replacement window, excluding provenance churn."""

from dataclasses import dataclass

import duckdb

from electricity_pipeline.source import REGION
from electricity_pipeline.validation import Batch


@dataclass(frozen=True)
class RowChanges:
    added: int
    changed: int
    removed: int
    unchanged: int


@dataclass(frozen=True)
class RevisionSummary:
    generation: RowChanges
    source_totals: RowChanges
    previous_retrieval_ids: tuple[str, ...]


def compare(previous: dict, incoming: dict) -> RowChanges:
    shared = previous.keys() & incoming.keys()
    changed = sum(previous[key] != incoming[key] for key in shared)
    return RowChanges(
        added=len(incoming.keys() - previous.keys()),
        changed=changed,
        removed=len(previous.keys() - incoming.keys()),
        unchanged=len(shared) - changed,
    )


def summarize(connection: duckdb.DuckDBPyConnection, batch: Batch) -> RevisionSummary:
    """Call inside the load transaction, before replacing any observations."""
    bounds = [REGION, batch.window.start, batch.window.end]
    observations = connection.execute(
        "SELECT day, technology_id, technology, renewable, energy_mwh, source_share, "
        "retrieval_id FROM generation WHERE region = ? AND day BETWEEN ? AND ?",
        bounds,
    ).fetchall()
    totals = connection.execute(
        "SELECT day, total_mwh, retrieval_id FROM source_totals "
        "WHERE region = ? AND day BETWEEN ? AND ?",
        bounds,
    ).fetchall()
    previous = {(row[0], row[1]): row[2:6] for row in observations}
    incoming = {
        (row.day, row.technology_id): (
            row.technology,
            row.renewable,
            row.energy_mwh,
            float(row.source_share) if row.source_share is not None else None,
        )
        for row in batch.observations
    }
    return RevisionSummary(
        generation=compare(previous, incoming),
        source_totals=compare({row[0]: row[1] for row in totals}, batch.totals),
        previous_retrieval_ids=tuple(sorted({row[-1] for row in observations + totals})),
    )
