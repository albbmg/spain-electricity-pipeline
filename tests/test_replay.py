"""Offline recovery and integrity checks using explicitly synthetic source examples."""

import json
from dataclasses import asdict, replace
from datetime import UTC, date, datetime

import pytest

from electricity_pipeline import cli
from electricity_pipeline.replay import read_manifest
from electricity_pipeline.source import Window, archive
from electricity_pipeline.validation import parse
from electricity_pipeline.warehouse import connect, load, quality


@pytest.fixture
def archived(tmp_path, payload_factory, encode):
    window = Window(date(2025, 3, 29), date(2025, 3, 31))
    body = encode(payload_factory(window))
    retrieval = archive(body, window, tmp_path / "raw")
    # An intentionally old, synthetic acquisition time makes accidental replacement visible.
    retrieval = replace(retrieval, retrieved_at="2026-01-11T00:00:00+00:00")
    manifest = tmp_path / "raw" / f"{retrieval.retrieval_id}.manifest.json"
    manifest.write_text(json.dumps(asdict(retrieval)), encoding="utf-8")
    return manifest, parse(body, window), retrieval


def test_cli_replay_is_offline_repeatable_and_preserves_source_evidence(
    archived, tmp_path, monkeypatch
):
    manifest, batch, retrieval = archived
    original_files = {path.name: path.read_bytes() for path in manifest.parent.iterdir()}

    def unexpected_network(*args, **kwargs):
        pytest.fail("Offline replay must not call the API")

    monkeypatch.setattr(cli, "fetch", unexpected_network)
    database = tmp_path / "replayed.duckdb"
    arguments = [
        "--replay-manifest",
        str(manifest),
        "--database",
        str(database),
        "--export-dir",
        str(tmp_path / "exports"),
    ]
    before = datetime.now(UTC)
    assert cli.main(arguments) == 0
    first_export = (tmp_path / "exports" / "daily_mix.csv").read_bytes()
    assert cli.main(arguments) == 0
    after = datetime.now(UTC)
    assert (tmp_path / "exports" / "daily_mix.csv").read_bytes() == first_export
    assert {path.name: path.read_bytes() for path in manifest.parent.iterdir()} == original_files

    with connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM generation").fetchone() == (6,)
        assert connection.execute("SELECT COUNT(*) FROM ingestion_runs").fetchone() == (1,)
        recorded = connection.execute("SELECT retrieved_at FROM ingestion_runs").fetchone()[0]
        assert recorded == datetime.fromisoformat(retrieval.retrieved_at)
        replays = connection.execute("SELECT replayed_at FROM replay_runs").fetchall()
        assert len(replays) == 2
        assert all(before <= stamp <= after for (stamp,) in replays)
        assert connection.execute(
            "SELECT DISTINCT day FROM generation ORDER BY day"
        ).fetchall() == [(day,) for day in sorted(batch.window.dates)]
        assert all(count == 0 for _, count in quality(connection))


def test_modified_payload_fails_before_database_or_exports_are_created(archived, tmp_path):
    manifest, _, retrieval = archived
    raw_path = manifest.parent / retrieval.raw_file
    raw_path.write_bytes(raw_path.read_bytes() + b" ")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        read_manifest(manifest)
    database = tmp_path / "untouched.duckdb"
    exports = tmp_path / "untouched-exports"
    assert (
        cli.main(
            [
                "--replay-manifest",
                str(manifest),
                "--database",
                str(database),
                "--export-dir",
                str(exports),
            ]
        )
        == 1
    )
    assert not database.exists()
    assert not exports.exists()


@pytest.mark.parametrize(
    "field,value",
    [
        ("sha256", "not-a-digest"),
        ("retrieval_id", "not-an-id"),
        ("region", "national"),
        ("start_date", "20250329"),
        ("end_date", "2025-04-01"),
        ("url", "https://example.com/unrelated"),
        ("retrieved_at", "2026-01-11T00:00:00"),
        ("retrieved_at", "2026-01-11T00:00:00+01:00"),
        ("raw_file", "../outside.json"),
        ("raw_file", "/tmp/outside.json"),
        ("raw_file", "..\\outside.json"),
        ("region", None),
    ],
)
def test_inconsistent_manifest_is_rejected(archived, field, value):
    manifest, _, _ = archived
    metadata = json.loads(manifest.read_text())
    metadata[field] = value
    manifest.write_text(json.dumps(metadata))
    with pytest.raises(ValueError):
        read_manifest(manifest)


@pytest.mark.parametrize(
    "case", ["missing-field", "unknown-field", "duplicate-field", "not-object"]
)
def test_ambiguous_manifest_schema_is_rejected(archived, case):
    manifest, _, _ = archived
    metadata = json.loads(manifest.read_text())
    if case == "missing-field":
        metadata.pop("sha256")
    elif case == "unknown-field":
        metadata["another_field"] = "unexpected"
    elif case == "not-object":
        metadata = list(metadata.values())
    text = json.dumps(metadata)
    if case == "duplicate-field":
        text = '{"region": "peninsular",' + text[1:]
    manifest.write_text(text)
    with pytest.raises(ValueError):
        read_manifest(manifest)


def test_symlink_payload_is_rejected(archived, tmp_path):
    manifest, _, retrieval = archived
    raw = manifest.parent / retrieval.raw_file
    outside = tmp_path / "outside.json"
    raw.rename(outside)
    raw.symlink_to(outside)
    with pytest.raises(ValueError, match="symbolic link"):
        read_manifest(manifest)


def test_missing_payload_is_rejected(archived):
    manifest, _, retrieval = archived
    (manifest.parent / retrieval.raw_file).unlink()
    with pytest.raises(ValueError, match="missing"):
        read_manifest(manifest)


def test_correct_checksum_does_not_bypass_source_validation(tmp_path):
    window = Window(date(2025, 1, 1), date(2025, 1, 1))
    retrieval = archive(b'{"errors": [{"detail": "synthetic"}]}', window, tmp_path)
    with pytest.raises(ValueError, match="error object"):
        read_manifest(tmp_path / f"{retrieval.retrieval_id}.manifest.json")


def test_existing_warehouse_accepts_original_manifest_and_rejects_conflicting_identity(
    archived, tmp_path
):
    _, batch, retrieval = archived
    database = tmp_path / "existing.duckdb"
    with connect(database) as connection:
        load(connection, batch, retrieval)
        expected = connection.execute(
            "SELECT * FROM generation ORDER BY day, technology_id"
        ).fetchall()
        # Simulate the prior schema, which has no replay audit table.
        connection.execute("DROP TABLE replay_runs")
    with connect(database) as connection:
        load(connection, batch, retrieval, replay=True)
        conflicting = replace(retrieval, retrieved_at="2026-01-12T00:00:00+00:00")
        with pytest.raises(ValueError, match="conflicts"):
            load(connection, batch, conflicting, replay=True)
        assert (
            connection.execute("SELECT * FROM generation ORDER BY day, technology_id").fetchall()
            == expected
        )
        assert connection.execute("SELECT COUNT(*) FROM replay_runs").fetchone() == (1,)
        assert connection.execute("SELECT COUNT(*) FROM ingestion_runs").fetchone() == (1,)


def test_failed_replay_rolls_back_data_and_audit(archived, tmp_path):
    _, batch, retrieval = archived
    with connect(tmp_path / "test.duckdb") as connection:
        load(connection, batch, retrieval)
        broken = replace(batch, totals={day: value + 10 for day, value in batch.totals.items()})
        with pytest.raises(ValueError, match="quality checks failed"):
            load(connection, broken, retrieval, replay=True)
        assert connection.execute("SELECT COUNT(*) FROM replay_runs").fetchone() == (0,)
        assert all(count == 0 for _, count in quality(connection))


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["--start", "2025-01-01"],
        ["--end", "2025-01-01"],
        ["--replay-manifest", "unused", "--start", "2025-01-01"],
    ],
)
def test_cli_rejects_missing_or_conflicting_modes(args):
    with pytest.raises(SystemExit) as error:
        cli.main(args)
    assert error.value.code == 2
