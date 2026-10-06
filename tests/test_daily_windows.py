"""Explicit daily acquisition with synthetic source responses; no missing-value imputation."""

import json
from datetime import date
from decimal import Decimal

import pytest

from electricity_pipeline import cli
from electricity_pipeline.replay import read_manifest
from electricity_pipeline.source import Window, daily_windows
from electricity_pipeline.warehouse import connect, load, quality


@pytest.mark.parametrize(
    "start,end,expected",
    [
        (date(2024, 2, 28), date(2024, 3, 1), 3),
        (date(2024, 3, 30), date(2024, 4, 1), 3),
        (date(2024, 12, 31), date(2025, 1, 1), 2),
        (date.max, date.max, 1),
    ],
)
def test_daily_windows_keep_each_local_calendar_date_once(start, end, expected):
    windows = daily_windows(start, end)
    assert len(windows) == expected
    assert [w.start for w in windows] == sorted(Window(start, end).dates)
    assert all(w.start == w.end for w in windows)


def test_daily_windows_reject_reversed_range():
    with pytest.raises(ValueError):
        daily_windows(date(2025, 1, 2), date(2025, 1, 1))


def arguments(tmp_path, mode="day"):
    return [
        "--start",
        "2024-03-17",
        "--end",
        "2024-03-19",
        "--request-window",
        mode,
        "--database",
        str(tmp_path / "live.duckdb"),
        "--raw-dir",
        str(tmp_path / "raw"),
        "--export-dir",
        str(tmp_path / "exports"),
    ]


def test_daily_source_series_are_preserved_without_inventing_rows(
    tmp_path, monkeypatch, payload_factory, encode
):
    calls = []

    def fetch(window):
        calls.append(window)
        # Source contains gas only on the middle day; no gas series on other days.
        payload = payload_factory(window, wind=100, gas=0)
        if window.start.day != 18:
            payload["included"].pop(1)
        return encode(payload)

    monkeypatch.setattr(cli, "fetch", fetch)
    assert cli.main(arguments(tmp_path)) == 0
    assert calls == daily_windows(date(2024, 3, 17), date(2024, 3, 19))
    with connect(tmp_path / "live.duckdb") as database:
        assert database.execute(
            "SELECT day, energy_mwh FROM generation WHERE technology_id = 'gas'"
        ).fetchall() == [(date(2024, 3, 18), Decimal(0))]
        assert database.execute("SELECT COUNT(*) FROM generation").fetchone() == (4,)
        assert database.execute("SELECT COUNT(*) FROM source_totals").fetchone() == (3,)
        assert database.execute("SELECT COUNT(*) FROM revision_runs").fetchone() == (3,)
        expected = database.execute(
            "SELECT * FROM generation ORDER BY day, technology_id"
        ).fetchall()
    manifests = list((tmp_path / "raw").glob("*.manifest.json"))
    assert len(manifests) == 3
    with connect(tmp_path / "replay.duckdb") as replay:
        for manifest in manifests:
            metadata = json.loads(manifest.read_text())
            assert metadata["start_date"] == metadata["end_date"]
            batch, retrieval = read_manifest(manifest)
            load(replay, batch, retrieval, replay=True)
        assert (
            replay.execute("SELECT * FROM generation ORDER BY day, technology_id").fetchall()
            == expected
        )
        assert all(count == 0 for _, count in quality(replay))


def test_failed_daily_window_stops_without_refreshing_exports(
    tmp_path, monkeypatch, payload_factory, encode
):
    calls = []
    export_dir = tmp_path / "exports"
    export_dir.mkdir()
    old_export = export_dir / "daily_mix.csv"
    old_export.write_text("explicitly synthetic prior export\n")

    def fetch(window):
        calls.append(window)
        payload = payload_factory(window)
        if window.start.day == 18:
            payload["included"][0]["attributes"]["values"] = []
        return encode(payload)

    monkeypatch.setattr(cli, "fetch", fetch)
    assert cli.main(arguments(tmp_path)) == 1
    assert [w.start.day for w in calls] == [17, 18]
    with connect(tmp_path / "live.duckdb") as database:
        assert database.execute("SELECT DISTINCT day FROM generation").fetchall() == [
            (date(2024, 3, 17),)
        ]
        assert database.execute("SELECT COUNT(*) FROM ingestion_runs").fetchone() == (1,)
    assert len(list((tmp_path / "raw").glob("*.manifest.json"))) == 2
    assert old_export.read_text() == "explicitly synthetic prior export\n"


@pytest.mark.parametrize("mode", ["day", "month"])
def test_replay_cannot_silently_ignore_request_window(mode):
    with pytest.raises(SystemExit) as error:
        cli.main(["--replay-manifest", "unused", "--request-window", mode])
    assert error.value.code == 2


def test_month_mode_retains_one_request_and_never_falls_back_automatically(
    tmp_path, monkeypatch, payload_factory, encode
):
    calls = []

    def fetch(window):
        calls.append(window)
        payload = payload_factory(window)
        payload["included"][1]["attributes"]["values"].pop()
        return encode(payload)

    monkeypatch.setattr(cli, "fetch", fetch)
    assert cli.main(arguments(tmp_path, "month")) == 1
    assert calls == [Window(date(2024, 3, 17), date(2024, 3, 19))]
