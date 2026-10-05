"""Explicitly synthetic contract examples; these are not observed REData values."""

import json
from datetime import datetime, time
from zoneinfo import ZoneInfo

import pytest


@pytest.fixture
def payload_factory():
    def make(window, *, wind=60, gas=40):
        dates = sorted(window.dates)
        updated = "2026-01-10T10:00:00+01:00"
        included = []
        for identity, title, category, energy in [
            ("wind", "Synthetic wind", "Renovable", wind),
            ("gas", "Synthetic gas", "No-Renovable", gas),
            ("total", "Synthetic total", "total", wind + gas),
        ]:
            included.append(
                {
                    "id": identity,
                    "attributes": {
                        "title": title,
                        "type": category,
                        "composite": False,
                        "last-update": updated,
                        "values": [
                            {
                                "value": energy,
                                "percentage": energy / (wind + gas),
                                "datetime": datetime.combine(
                                    day, time(), ZoneInfo("Europe/Madrid")
                                ).isoformat(),
                            }
                            for day in dates
                        ],
                    },
                }
            )
        return {
            "data": {"id": "gen1", "attributes": {"last-update": updated}},
            "included": included,
        }

    return make


@pytest.fixture
def encode():
    return lambda payload: json.dumps(payload).encode()
