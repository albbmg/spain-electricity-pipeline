import hashlib
import io
import json
from datetime import date
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse

import pytest

from electricity_pipeline.source import Window, archive, build_url, fetch, monthly_windows


def test_month_windows_cover_leap_day_once():
    start, end = date(2024, 1, 31), date(2024, 3, 1)
    windows = monthly_windows(start, end)
    assert len(windows) == 3
    assert sum(len(window.dates) for window in windows) == 31
    assert set().union(*(window.dates for window in windows)) == Window(start, end).dates


def test_geography_is_explicit_and_dates_inclusive():
    url = build_url(Window(date(2025, 1, 1), date(2025, 1, 31)))
    params = parse_qs(urlparse(url).query)
    assert params["geo_ids"] == ["8741"]
    assert params["geo_limit"] == ["peninsular"]
    assert params["time_trunc"] == ["day"]
    assert params["end_date"] == ["2025-01-31T23:59"]


def test_raw_archive_keeps_exact_bytes_and_unique_retrievals(tmp_path):
    body = b'{"synthetic": true}\n'
    window = Window(date(2025, 1, 1), date(2025, 1, 1))
    first = archive(body, window, tmp_path)
    second = archive(body, window, tmp_path)
    assert first.sha256 == second.sha256 == hashlib.sha256(body).hexdigest()
    assert first.retrieval_id != second.retrieval_id
    assert (tmp_path / first.raw_file).read_bytes() == body
    manifest = json.loads((tmp_path / f"{first.retrieval_id}.manifest.json").read_text())
    assert manifest["url"] == build_url(window)


class Response(io.BytesIO):
    headers = {"Content-Type": "application/json; charset=utf-8"}


def test_transient_error_is_retried_and_retry_after_respected():
    calls, delays = [], []

    def opener(request, timeout):
        calls.append((request, timeout))
        if len(calls) == 1:
            raise HTTPError(request.full_url, 429, "busy", {"Retry-After": "3"}, None)
        return Response(b"{}")

    assert (
        fetch(Window(date(2025, 1, 1), date(2025, 1, 1)), opener=opener, sleep=delays.append)
        == b"{}"
    )
    assert len(calls) == 2
    assert delays == [3]


@pytest.mark.parametrize(
    "status,retry_after,calls_expected", [(404, None, 1), (503, None, 3), (429, "120", 1)]
)
def test_terminal_errors_and_retry_bound(status, retry_after, calls_expected):
    calls = []

    def opener(request, timeout):
        calls.append(request)
        headers = {"Retry-After": retry_after} if retry_after else {}
        raise HTTPError(request.full_url, status, "test", headers, None)

    with pytest.raises(HTTPError):
        fetch(Window(date(2025, 1, 1), date(2025, 1, 1)), opener=opener, sleep=lambda _: None)
    assert len(calls) == calls_expected
