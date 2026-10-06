"""Historical comparisons over explicitly synthetic complete calendar years."""

import json
import shutil
from datetime import date, datetime, time
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from electricity_pipeline import history
from electricity_pipeline.source import archive, monthly_windows
from electricity_pipeline.validation import parse
from electricity_pipeline.warehouse import connect, load


@pytest.fixture(scope="module")
def history_path(tmp_path_factory):
    root = tmp_path_factory.mktemp("synthetic-history")
    path = root / "complete.duckdb"
    with connect(path) as connection:
        # Include a complete extra year to detect accidentally unbounded comparisons.
        for window in monthly_windows(date(2023, 1, 1), date(2025, 12, 31)):
            scale = 2 if window.start.year == 2025 else 1
            wind, gas = (90, 10) if window.start.month == 1 else (100, 900)
            updated = "2026-01-02T00:00:00+00:00"
            included = []
            for identity, kind, energy in [
                ("wind", "Renovable", wind * scale),
                ("gas", "No-Renovable", gas * scale),
                ("total", "total", (wind + gas) * scale),
            ]:
                included.append(
                    {
                        "id": identity,
                        "attributes": {
                            "title": f"Synthetic {identity}",
                            "type": kind,
                            "composite": False,
                            "last-update": updated,
                            "values": [
                                {
                                    "value": energy,
                                    "datetime": datetime.combine(
                                        day, time(), ZoneInfo("Europe/Madrid")
                                    ).isoformat(),
                                }
                                for day in sorted(window.dates)
                            ],
                        },
                    }
                )
            body = json.dumps(
                {
                    "data": {"id": "gen1", "attributes": {"last-update": updated}},
                    "included": included,
                }
            ).encode()
            load(connection, parse(body, window), archive(body, window, root / "raw"))
    return path


@pytest.fixture
def database(history_path, tmp_path):
    path = tmp_path / "history.duckdb"
    shutil.copy2(history_path, path)
    with connect(path) as connection:
        yield connection


def test_complete_years_use_energy_weighting_and_leap_calendar(database):
    result = history.periods(database, 2024, 2025)
    annual = [p for p in result if p.grain == "year"]
    assert [p.days for p in annual] == [366, 365]
    assert len([p for p in result if p.grain == "month"]) == 24
    assert len([p for p in result if p.grain == "quarter"]) == 8
    assert annual[0].generation_mwh == Decimal(31 * 100 + 335 * 1000)
    assert annual[0].share == Decimal(31 * 90 + 335 * 100) / annual[0].generation_mwh
    assert annual[0].share != Decimal("0.9") / 12 + Decimal("0.1") * 11 / 12
    february = [p for p in result if p.grain == "month" and p.start.month == 2]
    assert [p.days for p in february] == [29, 28]
    assert february[1].daily_mwh / february[0].daily_mwh == 2


@pytest.mark.parametrize(
    "condition",
    [
        "day = '2024-02-29'",
        "day BETWEEN '2024-06-01' AND '2024-06-30'",
        "day BETWEEN '2024-01-01' AND '2024-12-31'",
    ],
)
def test_incomplete_periods_are_rejected_even_when_remaining_days_reconcile(database, condition):
    # Fixed test predicates, never user-controlled SQL.
    database.execute(f"DELETE FROM generation WHERE {condition}")
    database.execute(f"DELETE FROM source_totals WHERE {condition}")
    with pytest.raises(ValueError, match="every day"):
        history.render(database, 2024, 2025)


@pytest.mark.parametrize("start,end", [(2025, 2025), (2025, 2024), (0, 2025), (2024, 9999)])
def test_invalid_year_ranges_fail(database, start, end):
    with pytest.raises(ValueError, match="complete past calendar years"):
        history.periods(database, start, end)


def test_report_matches_calendar_month_and_excludes_unselected_evidence(database):
    report = history.render(database, 2024, 2025)
    assert "**731 days**" in report
    assert "**1,462 technology observations**" in report
    assert "2023" not in report
    # February volume YoY differs from daily-average YoY because 2024 is a leap year.
    assert "| 2025-02 | 28 | 56.000 | 2.000 | 10.00% | +93.10% | +100.00% | +0.00 |" in report
    assert "| 2024-02 | 29 | 29.000 | 1.000 | 10.00% | — | — | — |" in report
    assert report.count("  - SHA-256:") == 24
    assert report.count("  - Retrieved at:") == 24
    assert report.count("  - Provider last update:") == 24
    assert "2024-Q1 | 91" in report
    assert "2025-Q1 | 90" in report
    assert "(2024-02) to **90.00%** (2024-01)" in report
    assert report == history.render(database, 2024, 2025)


def test_corrupt_warehouse_cannot_produce_report(database):
    database.execute("UPDATE source_totals SET total_mwh = 1 WHERE day = '2025-01-01'")
    with pytest.raises(ValueError, match="quality checks failed"):
        history.render(database, 2024, 2025)


def test_cli_is_read_only_and_outputs_complete_report(history_path, capsys):
    before = history_path.read_bytes()
    assert (
        history.main(
            ["--database", str(history_path), "--start-year", "2024", "--end-year", "2025"]
        )
        == 0
    )
    assert capsys.readouterr().out.startswith("# Peninsular generation: 2024–2025")
    assert history_path.read_bytes() == before


def test_cli_missing_database_does_not_create_it(tmp_path, capsys):
    missing = tmp_path / "missing.duckdb"
    assert (
        history.main(["--database", str(missing), "--start-year", "2024", "--end-year", "2025"])
        == 1
    )
    output = capsys.readouterr()
    assert output.out == ""
    assert "Historical report failed" in output.err
    assert not missing.exists()


def test_cli_incomplete_history_prints_no_partial_report(history_path, tmp_path, capsys):
    path = tmp_path / "incomplete.duckdb"
    shutil.copy2(history_path, path)
    with connect(path) as connection:
        connection.execute("DELETE FROM generation WHERE day = '2024-02-29'")
        connection.execute("DELETE FROM source_totals WHERE day = '2024-02-29'")
    assert (
        history.main(["--database", str(path), "--start-year", "2024", "--end-year", "2025"]) == 1
    )
    output = capsys.readouterr()
    assert output.out == ""
    assert "every day" in output.err
