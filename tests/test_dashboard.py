"""Offline dashboard contracts over explicitly synthetic calendar years."""

import json
import re
import shutil
from decimal import Decimal

import duckdb
import pytest
from test_history import history_path as history_path

from electricity_pipeline import dashboard


@pytest.fixture(scope="module")
def technology_path(history_path, tmp_path_factory):
    """Keep daily totals valid while exercising sparse and changing source series."""
    path = tmp_path_factory.mktemp("synthetic-technologies") / "technology.duckdb"
    shutil.copy2(history_path, path)
    with duckdb.connect(str(path)) as connection:
        connection.execute(
            "INSERT INTO generation SELECT region, day, 'rare', 'Synthetic wind', true, "
            "100, NULL, source_updated_at, retrieval_id FROM generation "
            "WHERE day = '2024-02-29' AND technology_id = 'gas'"
        )
        connection.execute(
            "UPDATE generation SET energy_mwh = energy_mwh - 100 "
            "WHERE day = '2024-02-29' AND technology_id = 'gas'"
        )
        connection.execute(
            "INSERT INTO generation SELECT region, day, 'zero', 'Synthetic measured zero', "
            "false, 0, NULL, source_updated_at, retrieval_id FROM generation "
            "WHERE day = '2024-02-29' AND technology_id = 'gas'"
        )
        connection.execute(
            "UPDATE generation SET technology = 'Synthetic renamed wind' "
            "WHERE technology_id = 'wind' AND day BETWEEN '2024-02-01' AND '2024-02-10'"
        )
        connection.execute(
            "UPDATE generation SET renewable = false "
            "WHERE technology_id = 'wind' AND day BETWEEN '2024-02-01' AND '2024-02-05'"
        )
        connection.execute(
            "UPDATE generation SET energy_mwh = 2000 WHERE technology_id = 'wind' "
            "AND day BETWEEN '2025-03-01' AND '2025-03-31'"
        )
        connection.execute(
            "DELETE FROM generation WHERE technology_id = 'gas' "
            "AND day BETWEEN '2025-03-01' AND '2025-03-31'"
        )
    return path


def test_technology_values_match_source_sql_and_reconcile_each_month(technology_path):
    with duckdb.connect(str(technology_path), read_only=True) as connection:
        result = dashboard.snapshot(connection, 2024, 2025)
        for row in result["selections"]["all"]["rows"]:
            expected = connection.execute(
                "SELECT technology_id, technology, renewable, COUNT(DISTINCT day), "
                "SUM(energy_mwh) FROM generation WHERE region = 'peninsular' "
                "AND strftime(day, '%Y-%m') = ? GROUP BY 1, 2, 3 "
                "ORDER BY SUM(energy_mwh) DESC, 1, 2, 3",
                [row["month"]],
            ).fetchall()
            technologies = row["technologies"]
            assert len(technologies) == len(expected)
            total = Decimal(row["generation_mwh"])
            assert sum(Decimal(t["generation_mwh"]) for t in technologies) == total
            for technology, (identity, name, renewable, days, energy) in zip(
                technologies, expected, strict=True
            ):
                assert technology["id"] == identity
                assert technology["name"] == name
                assert technology["renewable"] is renewable
                assert technology["days_observed"] == days
                assert Decimal(technology["generation_mwh"]) == energy
                assert technology["generation_gwh"] == f"{energy / 1000:,.3f}"
                assert technology["system_share"] == f"{energy / total:.2%}"
                assert identity != "total"
            assert row in result["selections"][row["month"][:4]]["rows"]
            assert not row["month"].startswith("2023")


def test_technology_coverage_distinguishes_sparse_zero_absent_and_changed_series(technology_path):
    with duckdb.connect(str(technology_path), read_only=True) as connection:
        selections = dashboard.snapshot(connection, 2024, 2025)["selections"]
    february = selections["2024"]["rows"][1]
    assert february["days"] == 29
    technologies = february["technologies"]
    rare = next(t for t in technologies if t["id"] == "rare")
    assert (rare["days_observed"], rare["generation_gwh"], rare["system_share"]) == (
        1,
        "0.100",
        "0.34%",
    )
    zero = next(t for t in technologies if t["id"] == "zero")
    assert (zero["days_observed"], zero["generation_gwh"], zero["system_share"]) == (
        1,
        "0.000",
        "0.00%",
    )
    variants = [t for t in technologies if t["id"] == "wind"]
    assert len(variants) == 3
    assert sorted(t["days_observed"] for t in variants) == [5, 5, 19]
    assert {t["renewable"] for t in variants} == {False, True}
    assert {t["name"] for t in variants} == {"Synthetic wind", "Synthetic renamed wind"}
    assert all(
        t["id"] not in {"rare", "zero"} for t in selections["2024"]["rows"][2]["technologies"]
    )
    assert [t["id"] for t in selections["2025"]["rows"][2]["technologies"]] == ["wind"]
    assert selections["2025"]["rows"][1]["technologies"][0]["days_observed"] == 28


def test_technology_html_for_browser_verification(technology_path, tmp_path):
    with duckdb.connect(str(technology_path), read_only=True) as connection:
        document = dashboard.render(connection, 2024, 2025)
    # This local verification artifact must never be confused with a source-data report.
    document = document.replace(
        "Spain Electricity Pipeline / Historical explorer", "Synthetic verification data"
    )
    (tmp_path / "synthetic-dashboard.html").write_text(document, encoding="utf-8")
    assert "Synthetic verification data" in document


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
        connection.execute("UPDATE generation SET technology = ?", [dangerous])
        document = dashboard.render(connection, 2024, 2025)
        assert document == dashboard.render(connection, 2024, 2025)
    assert dangerous not in document
    encoded = re.search(
        r'<script id="dashboard-data" type="application/json">(.*?)</script>', document
    )
    data = json.loads(encoded.group(1))
    assert data["selections"]["2024"]["evidence"][0][-1] == dangerous
    assert data["selections"]["2024"]["rows"][0]["technologies"][0]["name"] == dangerous
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
