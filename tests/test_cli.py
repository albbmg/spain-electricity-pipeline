from datetime import date

import pytest

from electricity_pipeline import cli
from electricity_pipeline.source import Window


def test_cli_runs_to_verified_exports_without_network(
    tmp_path, monkeypatch, payload_factory, encode
):
    def fake_fetch(window):
        return encode(payload_factory(window))

    monkeypatch.setattr(cli, "fetch", fake_fetch)
    arguments = [
        "--start",
        "2025-01-31",
        "--end",
        "2025-02-01",
        "--database",
        str(tmp_path / "test.duckdb"),
        "--raw-dir",
        str(tmp_path / "raw"),
        "--export-dir",
        str(tmp_path / "exports"),
    ]
    assert cli.main(arguments) == 0
    assert (tmp_path / "exports" / "monthly_mix.csv").exists()
    assert len(list((tmp_path / "raw").glob("*.manifest.json"))) == 2


def test_bad_payload_is_archived_but_does_not_export(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "fetch", lambda window: b'{"errors": [{"detail": "synthetic"}]}')
    arguments = [
        "--start",
        "2025-01-01",
        "--end",
        "2025-01-01",
        "--database",
        str(tmp_path / "test.duckdb"),
        "--raw-dir",
        str(tmp_path / "raw"),
        "--export-dir",
        str(tmp_path / "exports"),
    ]
    assert cli.main(arguments) == 1
    assert not (tmp_path / "exports").exists()
    assert len(list((tmp_path / "raw").glob("*.manifest.json"))) == 1


def test_reversed_window_rejected():
    with pytest.raises(ValueError):
        Window(date(2025, 2, 1), date(2025, 1, 1))


def test_future_date_is_rejected_before_any_network():
    with pytest.raises(SystemExit) as error:
        cli.main(["--start", "9999-01-01", "--end", "9999-01-01"])
    assert error.value.code == 2
