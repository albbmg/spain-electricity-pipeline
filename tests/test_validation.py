from copy import deepcopy
from datetime import date
from decimal import Decimal

import pytest

from electricity_pipeline.source import Window
from electricity_pipeline.validation import ContractError, parse

WINDOW = Window(date(2025, 1, 1), date(2025, 1, 2))


def test_total_is_not_a_technology_and_zero_is_preserved(payload_factory, encode):
    batch = parse(encode(payload_factory(WINDOW, wind=0, gas=100)), WINDOW)
    assert len(batch.observations) == 4
    assert sum(row.energy_mwh for row in batch.observations) == Decimal(200)
    assert len([row for row in batch.observations if row.energy_mwh == 0]) == 2
    assert all(row.technology_id != "total" for row in batch.observations)


@pytest.mark.parametrize(
    "start,end", [(date(2025, 3, 29), date(2025, 3, 31)), (date(2025, 10, 25), date(2025, 10, 27))]
)
def test_dst_keeps_local_calendar_dates(payload_factory, encode, start, end):
    window = Window(start, end)
    batch = parse(encode(payload_factory(window)), window)
    assert {row.day for row in batch.observations} == window.dates


def test_incomplete_series_is_rejected(payload_factory, encode):
    payload = payload_factory(WINDOW)
    payload["included"][0]["attributes"]["values"].pop()
    with pytest.raises(ContractError, match="Incomplete date"):
        parse(encode(payload), WINDOW)


def test_duplicate_day_is_rejected(payload_factory, encode):
    payload = payload_factory(WINDOW)
    values = payload["included"][0]["attributes"]["values"]
    values.append(deepcopy(values[0]))
    with pytest.raises(ContractError, match="Duplicate observation"):
        parse(encode(payload), WINDOW)


@pytest.mark.parametrize("bad", [-1, True, None, "60", float("nan"), float("inf"), 0.0000001])
def test_invalid_energy_fails_before_loading(payload_factory, encode, bad):
    payload = payload_factory(WINDOW)
    payload["included"][0]["attributes"]["values"][0]["value"] = bad
    with pytest.raises(ContractError):
        parse(encode(payload), WINDOW)


def test_material_total_mismatch_fails(payload_factory, encode):
    payload = payload_factory(WINDOW)
    payload["included"][-1]["attributes"]["values"][0]["value"] = 110
    with pytest.raises(ContractError, match="does not reconcile"):
        parse(encode(payload), WINDOW)


def test_unknown_category_is_not_silently_classified(payload_factory, encode):
    payload = payload_factory(WINDOW)
    payload["included"][0]["attributes"]["type"] = "new-category"
    with pytest.raises(ContractError, match="Unrecognised"):
        parse(encode(payload), WINDOW)


@pytest.mark.parametrize(
    "stamp", ["2025-01-01T00:00:00", "2025-01-01T00:00:00+00:00", "2025-01-01T01:00:00+01:00"]
)
def test_wrong_timezone_or_grain_is_rejected(payload_factory, encode, stamp):
    payload = payload_factory(WINDOW)
    payload["included"][0]["attributes"]["values"][0]["datetime"] = stamp
    with pytest.raises(ContractError):
        parse(encode(payload), WINDOW)


@pytest.mark.parametrize(
    "case",
    ["missing_total", "duplicate_total", "duplicate_series", "wrong_widget", "error_response"],
)
def test_ambiguous_response_fails(payload_factory, encode, case):
    payload = payload_factory(WINDOW)
    if case == "missing_total":
        payload["included"].pop()
    elif case == "duplicate_total":
        extra = deepcopy(payload["included"][-1])
        extra["id"] = "another-total"
        payload["included"].append(extra)
    elif case == "duplicate_series":
        payload["included"].append(deepcopy(payload["included"][0]))
    elif case == "wrong_widget":
        payload["data"]["id"] = "demand"
    else:
        payload = {"errors": [{"detail": "Synthetic service error"}]}
    with pytest.raises(ContractError):
        parse(encode(payload), WINDOW)
