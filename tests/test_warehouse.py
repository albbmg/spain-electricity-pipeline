from dataclasses import replace
from datetime import date
from decimal import Decimal

import duckdb
import pytest

from electricity_pipeline.source import Window, archive
from electricity_pipeline.validation import parse
from electricity_pipeline.warehouse import connect, export_csv, load, quality


@pytest.fixture
def connection(tmp_path):
    with connect(tmp_path / "test.duckdb") as database:
        yield database


def ingest(connection, tmp_path, window, payload):
    import json

    body = json.dumps(payload).encode()
    retrieval = archive(body, window, tmp_path / "raw")
    batch = parse(body, window)
    load(connection, batch, retrieval)
    return batch, retrieval


def test_repeat_load_keeps_row_counts_and_energy(connection, tmp_path, payload_factory):
    window = Window(date(2025, 1, 1), date(2025, 1, 2))
    for _ in range(2):
        ingest(connection, tmp_path, window, payload_factory(window))
    assert connection.execute("SELECT COUNT(*), SUM(energy_mwh) FROM generation").fetchone() == (
        4,
        Decimal(200),
    )
    assert connection.execute("SELECT COUNT(*) FROM ingestion_runs").fetchone()[0] == 2
    assert all(count == 0 for _, count in quality(connection))


def test_revision_replaces_only_requested_days(connection, tmp_path, payload_factory):
    window = Window(date(2025, 1, 1), date(2025, 1, 2))
    ingest(connection, tmp_path, window, payload_factory(window))
    revised = Window(window.end, window.end)
    ingest(connection, tmp_path, revised, payload_factory(revised, wind=80, gas=20))
    values = connection.execute("SELECT renewable_share FROM daily_mix ORDER BY day").fetchall()
    assert values == [(0.6,), (0.8,)]
    assert connection.execute("SELECT COUNT(*) FROM generation").fetchone()[0] == 4


def test_removed_technology_does_not_survive_partition_replacement(
    connection, tmp_path, payload_factory
):
    window = Window(date(2025, 1, 1), date(2025, 1, 1))
    ingest(connection, tmp_path, window, payload_factory(window))
    revised = payload_factory(window, wind=100, gas=0)
    revised["included"].pop(1)
    ingest(connection, tmp_path, window, revised)
    assert connection.execute("SELECT technology_id FROM generation").fetchall() == [("wind",)]
    assert connection.execute("SELECT generation_mwh FROM daily_mix").fetchone()[0] == Decimal(100)


def test_insert_failure_rolls_back_deletion(connection, tmp_path, payload_factory):
    window = Window(date(2025, 1, 1), date(2025, 1, 1))
    batch, retrieval = ingest(connection, tmp_path, window, payload_factory(window))
    # Reusing a retrieval ID violates the audit-table primary key after deletion begins.
    with pytest.raises(duckdb.ConstraintException):
        load(connection, batch, retrieval)
    assert connection.execute("SELECT COUNT(*) FROM generation").fetchone()[0] == 2
    assert connection.execute("SELECT COUNT(*) FROM ingestion_runs").fetchone()[0] == 1


def test_quality_failure_rolls_back_replacement(connection, tmp_path, payload_factory):
    window = Window(date(2025, 1, 1), date(2025, 1, 1))
    batch, retrieval = ingest(connection, tmp_path, window, payload_factory(window))
    broken_row = replace(batch.observations[0], energy_mwh=Decimal(10))
    broken = replace(batch, observations=(broken_row, batch.observations[1]))
    with pytest.raises(ValueError, match="quality checks failed"):
        load(connection, broken, replace(retrieval, retrieval_id="synthetic-failed-load"))
    assert connection.execute("SELECT SUM(energy_mwh) FROM generation").fetchone()[0] == Decimal(
        100
    )
    assert connection.execute("SELECT COUNT(*) FROM ingestion_runs").fetchone()[0] == 1


def test_monthly_share_is_energy_weighted_and_partial_month_is_visible(
    connection, tmp_path, payload_factory
):
    window = Window(date(2025, 1, 1), date(2025, 1, 1))
    ingest(connection, tmp_path, window, payload_factory(window, wind=90, gas=10))
    other = Window(date(2025, 1, 2), date(2025, 1, 2))
    ingest(connection, tmp_path, other, payload_factory(other, wind=10, gas=890))
    row = connection.execute(
        "SELECT renewable_share, days_observed, is_complete_month FROM monthly_mix"
    ).fetchone()
    assert row == (0.1, 2, False)


def test_full_leap_month_is_complete_and_exports_match(connection, tmp_path, payload_factory):
    window = Window(date(2024, 2, 1), date(2024, 2, 29))
    ingest(connection, tmp_path, window, payload_factory(window))
    assert connection.execute("SELECT is_complete_month FROM monthly_mix").fetchone() == (True,)
    outputs = export_csv(connection, tmp_path / "exports")
    assert len(outputs) == 3
    text = (tmp_path / "exports" / "daily_mix.csv").read_text()
    assert len(text.splitlines()) == 30
    assert "source_sha256" in text.splitlines()[0]


def test_empty_database_cannot_mask_orphan_generation(connection):
    connection.execute(
        "INSERT INTO generation VALUES "
        "('peninsular', '2025-01-01', 'x', 'synthetic', true, 1, 1, "
        "'2025-01-02T00:00:00+00:00', 'missing')"
    )
    with pytest.raises(ValueError, match="quality checks failed"):
        quality(connection)
