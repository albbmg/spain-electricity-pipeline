"""Revision semantics using explicitly synthetic source examples and local DuckDB."""

from dataclasses import replace
from datetime import UTC, date, datetime

import duckdb
import pytest

from electricity_pipeline import cli, warehouse
from electricity_pipeline.revisions import RowChanges
from electricity_pipeline.source import Window, archive
from electricity_pipeline.validation import parse
from electricity_pipeline.warehouse import connect, load, quality


@pytest.fixture
def connection(tmp_path):
    with connect(tmp_path / "test.duckdb") as database:
        yield database


@pytest.fixture
def ingest(tmp_path, payload_factory, encode):
    def run(connection, window, payload=None):
        body = encode(payload if payload is not None else payload_factory(window))
        retrieval = archive(body, window, tmp_path / "raw")
        batch = parse(body, window)
        return load(connection, batch, retrieval), batch, retrieval

    return run


def test_initial_and_unchanged_load_keep_separate_events(connection, ingest):
    window = Window(date(2025, 1, 1), date(2025, 1, 2))
    before = datetime.now(UTC)
    initial, _, first = ingest(connection, window)
    repeated, _, second = ingest(connection, window)
    assert initial.generation == RowChanges(4, 0, 0, 0)
    assert initial.source_totals == RowChanges(2, 0, 0, 0)
    assert initial.previous_retrieval_ids == ()
    assert repeated.generation == RowChanges(0, 0, 0, 4)
    assert repeated.source_totals == RowChanges(0, 0, 0, 2)
    assert repeated.previous_retrieval_ids == (first.retrieval_id,)
    rows = connection.execute(
        "SELECT retrieval_id, loaded_at, mode FROM revision_runs ORDER BY loaded_at"
    ).fetchall()
    assert [row[0] for row in rows] == [first.retrieval_id, second.retrieval_id]
    assert all(before <= row[1] <= datetime.now(UTC) and row[2] == "live" for row in rows)


def test_partial_overlap_uses_all_previous_retrievals_and_preserves_outside_days(
    connection, ingest, payload_factory
):
    first_window = Window(date(2025, 1, 1), date(2025, 1, 2))
    _, _, first = ingest(connection, first_window)
    _, _, second = ingest(connection, Window(date(2025, 1, 3), date(2025, 1, 3)))
    outside = connection.execute("SELECT * FROM generation WHERE day = '2025-01-01'").fetchall()
    overlap = Window(date(2025, 1, 2), date(2025, 1, 4))
    summary, _, _ = ingest(connection, overlap, payload_factory(overlap, wind=80, gas=20))
    assert summary.generation == RowChanges(2, 4, 0, 0)
    assert summary.source_totals == RowChanges(1, 0, 0, 2)
    assert summary.previous_retrieval_ids == tuple(
        sorted([first.retrieval_id, second.retrieval_id])
    )
    assert (
        connection.execute("SELECT * FROM generation WHERE day = '2025-01-01'").fetchall()
        == outside
    )


def test_replaced_technology_is_added_and_removed_not_changed(connection, ingest, payload_factory):
    window = Window(date(2025, 1, 1), date(2025, 1, 1))
    ingest(connection, window)
    revised = payload_factory(window)
    revised["included"][1]["id"] = "new-gas-id"
    summary, _, _ = ingest(connection, window, revised)
    assert summary.generation == RowChanges(1, 0, 1, 1)
    assert summary.source_totals == RowChanges(0, 0, 0, 1)


@pytest.mark.parametrize("field", ["title", "type", "percentage", "null-percentage", "value"])
def test_business_value_changes_are_counted(connection, ingest, payload_factory, field):
    window = Window(date(2025, 1, 1), date(2025, 1, 1))
    ingest(connection, window)
    revised = payload_factory(window)
    attributes = revised["included"][0]["attributes"]
    if field == "title":
        attributes[field] = "Renamed synthetic wind"
    elif field == "type":
        attributes[field] = "No-Renovable"
    elif field in {"percentage", "null-percentage"}:
        attributes["values"][0]["percentage"] = None if field == "null-percentage" else 0.61
    else:
        # Small exact energy change with unchanged percentage still counts.
        attributes["values"][0]["value"] = 60.000001
        revised["included"][2]["attributes"]["values"][0]["value"] = 100.000001
    summary, _, _ = ingest(connection, window, revised)
    assert summary.generation == RowChanges(0, 1, 0, 1)
    assert summary.source_totals == (
        RowChanges(0, 1, 0, 0) if field == "value" else RowChanges(0, 0, 0, 1)
    )


def test_publication_timestamp_alone_is_not_a_value_revision(connection, ingest, payload_factory):
    window = Window(date(2025, 1, 1), date(2025, 1, 1))
    ingest(connection, window)
    revised = payload_factory(window)
    revised["data"]["attributes"]["last-update"] = "2026-01-12T12:00:00+01:00"
    for series in revised["included"]:
        series["attributes"]["last-update"] = "2026-01-12T12:00:00+01:00"
    summary, _, _ = ingest(connection, window, revised)
    assert summary.generation == RowChanges(0, 0, 0, 2)
    assert summary.source_totals == RowChanges(0, 0, 0, 1)


def test_quality_failure_keeps_existing_audit_and_data(connection, ingest):
    window = Window(date(2025, 1, 1), date(2025, 1, 1))
    _, batch, retrieval = ingest(connection, window)
    audit = connection.execute("SELECT * FROM revision_runs").fetchall()
    data = connection.execute("SELECT * FROM generation").fetchall()
    broken = replace(batch, totals={window.start: 200})
    with pytest.raises(ValueError, match="quality checks failed"):
        load(connection, broken, retrieval, replay=True)
    assert connection.execute("SELECT * FROM revision_runs").fetchall() == audit
    assert connection.execute("SELECT * FROM generation").fetchall() == data
    assert connection.execute("SELECT COUNT(*) FROM replay_runs").fetchone() == (0,)


def test_audit_write_failure_rolls_back_load(connection, ingest, monkeypatch):
    window = Window(date(2025, 1, 1), date(2025, 1, 1))
    summary, batch, retrieval = ingest(connection, window)
    # Force an audit constraint failure after data insertion and quality validation.
    monkeypatch.setattr(
        warehouse, "summarize", lambda *_: replace(summary, generation=RowChanges(-1, 0, 0, 0))
    )
    with pytest.raises(duckdb.ConstraintException):
        load(connection, batch, replace(retrieval, retrieval_id="synthetic-failed-audit"))
    assert connection.execute("SELECT COUNT(*) FROM revision_runs").fetchone() == (1,)
    assert connection.execute("SELECT COUNT(*) FROM ingestion_runs").fetchone() == (1,)
    assert connection.execute("SELECT DISTINCT retrieval_id FROM generation").fetchall() == [
        (retrieval.retrieval_id,)
    ]
    quality(connection)


def test_old_warehouse_starts_audit_at_next_load_without_backfilling(tmp_path, ingest):
    path = tmp_path / "older.duckdb"
    window = Window(date(2025, 1, 1), date(2025, 1, 1))
    with connect(path) as connection:
        _, batch, retrieval = ingest(connection, window)
        connection.execute("DROP TABLE revision_runs")
    with connect(path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM revision_runs").fetchone() == (0,)
        assert connection.execute("SELECT COUNT(*) FROM generation").fetchone() == (2,)
        result = load(connection, batch, retrieval, replay=True)
        assert result.generation == RowChanges(0, 0, 0, 2)
        assert connection.execute("SELECT mode FROM revision_runs").fetchone() == ("replay",)
        assert connection.execute("SELECT loaded_at FROM revision_runs").fetchone() == (
            connection.execute("SELECT replayed_at FROM replay_runs").fetchone()
        )


def test_cli_replay_emits_persisted_summary(tmp_path, ingest, connection, capsys):
    import json

    window = Window(date(2025, 1, 1), date(2025, 1, 1))
    _, _, retrieval = ingest(connection, window)
    arguments = [
        "--replay-manifest",
        str(tmp_path / "raw" / f"{retrieval.retrieval_id}.manifest.json"),
        "--database",
        str(tmp_path / "cli.duckdb"),
        "--export-dir",
        str(tmp_path / "exports"),
    ]
    for expected in [RowChanges(2, 0, 0, 0), RowChanges(0, 0, 0, 2)]:
        assert cli.main(arguments) == 0
        output = capsys.readouterr().out.splitlines()
        summary = json.loads(next(line for line in output if line.startswith('{"revision"')))
        assert RowChanges(**summary["revision"]["generation"]) == expected
    with connect(tmp_path / "cli.duckdb") as database:
        assert database.execute("SELECT COUNT(*) FROM revision_runs").fetchone() == (2,)
        assert database.execute("SELECT COUNT(*) FROM ingestion_runs").fetchone() == (1,)
