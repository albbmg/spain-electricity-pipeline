"""Offline dashboard contracts over explicitly synthetic calendar years."""

import json
import re
import shutil
from decimal import Decimal

import duckdb
import pytest
from test_history import history_path as history_path

from electricity_pipeline import dashboard


def test_snapshot_weights_energy_and_keeps_published_total_separate(history_path):
    with duckdb.connect(str(history_path), read_only=True) as connection:
        result = dashboard.snapshot(connection, 2024, 2025)
    assert result["default"] == "2025"
    assert set(result["selections"]) == {"all", "2024", "2025"}
    annual = result["selections"]["2024"]
    energy = Decimal(31 * 100 + 335 * 1000)
    renewable = Decimal(31 * 90 + 335 * 100)
    assert annual["generation_gwh"] == f"{energy / 1000:,.3f}"
    assert annual["published_gwh"] == annual["generation_gwh"]
    assert annual["renewable_share"] == f"{renewable / energy:.2%}"
    assert annual["days"] == 366
    assert annual["rows"][1]["days"] == 29
    assert len(annual["evidence"]) == 12
    assert all(row[1].startswith("2024-") for row in annual["evidence"])
    assert result["selections"]["all"]["days"] == 731
    assert result["selections"]["all"]["months"] == 24
    assert result["selections"]["2025"]["rows"][1]["days"] == 28


@pytest.mark.parametrize("damage", ["gap", "unreconciled"])
def test_dashboard_rejects_invalid_history(history_path, tmp_path, damage):
    path = tmp_path / "bad.duckdb"
    shutil.copy2(history_path, path)
    with duckdb.connect(str(path)) as connection:
        if damage == "gap":
            connection.execute("DELETE FROM generation WHERE day = '2024-02-29'")
            connection.execute("DELETE FROM source_totals WHERE day = '2024-02-29'")
        else:
            connection.execute("UPDATE source_totals SET total_mwh = 1")
        with pytest.raises(ValueError):
            dashboard.render(connection, 2024, 2025)


def test_html_embeds_json_safely_and_renders_deterministically(history_path, tmp_path):
    path = tmp_path / "escaped.duckdb"
    shutil.copy2(history_path, path)
    dangerous = '</script><script>alert("synthetic")</script>'
    with duckdb.connect(str(path)) as connection:
        connection.execute("UPDATE ingestion_runs SET sha256 = ?", [dangerous])
        document = dashboard.render(connection, 2024, 2025)
        assert document == dashboard.render(connection, 2024, 2025)
    assert dangerous not in document
    encoded = re.search(
        r'<script id="dashboard-data" type="application/json">(.*?)</script>', document
    )
    data = json.loads(encoded.group(1))
    assert data["selections"]["2024"]["evidence"][0][-1] == dangerous
    assert "__DASHBOARD_DATA__" not in document
    assert "https://www.ree.es/es/aviso-legal" in document
    assert "<script src=" not in document


def test_cli_read_only_atomic_output_and_failure_preserves_existing(history_path, tmp_path):
    output = tmp_path / "dashboard.html"
    before = history_path.read_bytes()
    args = [
        "--database",
        str(history_path),
        "--start-year",
        "2024",
        "--end-year",
        "2025",
        "--output",
        str(output),
    ]
    assert dashboard.main(args) == 0
    document = output.read_bytes()
    assert document.startswith(b"<!doctype html>")
    assert history_path.read_bytes() == before
    args[3] = "2025"  # One year cannot pass the historical comparison contract.
    assert dashboard.main(args) == 1
    assert output.read_bytes() == document
    assert list(tmp_path.iterdir()) == [output]


def test_cli_missing_database_does_not_create_it(tmp_path):
    missing = tmp_path / "missing.duckdb"
    output = tmp_path / "dashboard.html"
    assert (
        dashboard.main(
            [
                "--database",
                str(missing),
                "--start-year",
                "2024",
                "--end-year",
                "2025",
                "--output",
                str(output),
            ]
        )
        == 1
    )
    assert not missing.exists()
    assert not output.exists()


def test_cli_cannot_overwrite_warehouse_even_with_html_extension(history_path, tmp_path):
    path = tmp_path / "warehouse.html"
    shutil.copy2(history_path, path)
    before = path.read_bytes()
    assert (
        dashboard.main(
            [
                "--database",
                str(path),
                "--start-year",
                "2024",
                "--end-year",
                "2025",
                "--output",
                str(path),
            ]
        )
        == 1
    )
    assert path.read_bytes() == before
