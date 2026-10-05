"""Validate source grain and totals before any database mutation."""

import json
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

from electricity_pipeline.source import Window

MADRID = ZoneInfo("Europe/Madrid")
ZERO = Decimal(0)
PRECISION = Decimal("0.000001")


class ContractError(ValueError):
    """A source response cannot support the declared analytical contract."""


@dataclass(frozen=True)
class Observation:
    day: date
    technology_id: str
    technology: str
    renewable: bool
    energy_mwh: Decimal
    source_share: Decimal | None
    source_updated_at: str


@dataclass(frozen=True)
class Batch:
    window: Window
    observations: tuple[Observation, ...]
    totals: dict[date, Decimal]
    source_updated_at: str


def amount(value, name: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, Decimal)):
        raise ContractError(f"{name} must be a JSON number")
    number = Decimal(value)
    if not number.is_finite() or number < 0 or number >= Decimal("1e18"):
        raise ContractError(f"{name} must be a finite, non-negative representable number")
    if number != number.quantize(PRECISION):
        raise ContractError(f"{name} has more than six decimal places")
    return number


def aware_timestamp(value, name: str) -> datetime:
    if not isinstance(value, str):
        raise ContractError(f"{name} must be an ISO timestamp")
    try:
        stamp = datetime.fromisoformat(value)
    except ValueError as error:
        raise ContractError(f"Invalid {name}: {value!r}") from error
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ContractError(f"{name} must include its UTC offset")
    return stamp


def observation_day(value) -> date:
    stamp = aware_timestamp(value, "observation datetime")
    local = stamp.astimezone(MADRID)
    if stamp.time() != time(0) or local.time() != time(0):
        raise ContractError("Daily observations must be midnight in Europe/Madrid")
    if stamp.utcoffset() != local.utcoffset():
        raise ContractError("Source offset does not match Europe/Madrid")
    return local.date()


def reject_constant(value):
    raise ContractError(f"Invalid JSON numeric constant: {value}")


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def parse(body: bytes, window: Window) -> Batch:
    """Reject incomplete or ambiguous source data; never invent missing observations."""
    try:
        payload = json.loads(
            body,
            parse_float=Decimal,
            parse_constant=reject_constant,
            object_pairs_hook=reject_duplicate_keys,
        )
        return _parse_payload(payload, window)
    except ContractError:
        raise
    except (KeyError, TypeError, ValueError, InvalidOperation, AttributeError) as error:
        raise ContractError(f"Malformed REData response: {error}") from error


def _parse_payload(payload, window: Window) -> Batch:
    if payload.get("errors"):
        raise ContractError("REData returned an error object")
    if payload["data"]["id"] != "gen1":
        raise ContractError("Unexpected REData widget; expected generation structure")
    updated = payload["data"]["attributes"]["last-update"]
    aware_timestamp(updated, "widget last-update")
    included = payload["included"]
    if not isinstance(included, list) or not included:
        raise ContractError("No generation series returned")

    observations = []
    totals = {}
    series_ids = set()
    total_seen = False
    sums = dict.fromkeys(window.dates, ZERO)
    for series in included:
        series_id = series["id"]
        if not isinstance(series_id, str) or not series_id or series_id in series_ids:
            raise ContractError("Missing or duplicate source series ID")
        series_ids.add(series_id)
        attributes = series["attributes"]
        kind = attributes["type"]
        if kind not in {"Renovable", "No-Renovable", "total"}:
            raise ContractError(f"Unrecognised generation category: {kind!r}")
        if attributes.get("composite") is not False:
            raise ContractError("Unexpected composite generation series")
        title = attributes["title"]
        if not isinstance(title, str) or not title.strip():
            raise ContractError("Missing technology name")
        series_updated = attributes["last-update"]
        aware_timestamp(series_updated, "series last-update")
        if kind == "total":
            if total_seen:
                raise ContractError("More than one generation total series")
            total_seen = True
        seen = set()
        for value in attributes["values"]:
            day = observation_day(value["datetime"])
            if day not in window.dates or day in seen:
                raise ContractError("Duplicate observation or date outside requested window")
            seen.add(day)
            energy = amount(value["value"], "energy_mwh")
            share = value.get("percentage")
            if share is not None:
                if isinstance(share, bool) or not isinstance(share, (int, Decimal)):
                    raise ContractError("Source share must be a JSON number or null")
                share = Decimal(share)
                if not share.is_finite() or not ZERO <= share <= 1:
                    raise ContractError("Source share must be between zero and one")
            if kind == "total":
                if energy <= 0:
                    raise ContractError("Published generation total must be positive")
                totals[day] = energy
            else:
                observations.append(
                    Observation(
                        day, series_id, title, kind == "Renovable", energy, share, series_updated
                    )
                )
                sums[day] += energy
        if seen != window.dates:
            raise ContractError(f"Incomplete date coverage for {title!r}")

    if not total_seen or not observations:
        raise ContractError("Expected technologies and exactly one total series")
    for day, total in totals.items():
        tolerance = max(Decimal("0.1"), total * Decimal("0.000001"))
        if abs(sums[day] - total) > tolerance:
            raise ContractError(f"Generation does not reconcile on {day}: {sums[day]} vs {total}")
    return Batch(window, tuple(observations), totals, updated)
