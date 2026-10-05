"""Bounded, read-only REData requests and immutable retrieval evidence."""

import calendar
import hashlib
import json
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ENDPOINT = "https://apidatos.ree.es/es/datos/generacion/estructura-generacion"
REGION = "peninsular"
RETRY_STATUSES = {429, 500, 502, 503, 504}
MAX_RESPONSE_BYTES = 10_000_000


@dataclass(frozen=True)
class Window:
    start: date
    end: date

    def __post_init__(self):
        if self.start > self.end:
            raise ValueError("start must be on or before end")

    @property
    def dates(self) -> set[date]:
        return {self.start + timedelta(days=i) for i in range((self.end - self.start).days + 1)}


def monthly_windows(start: date, end: date) -> list[Window]:
    """Partition an inclusive range without gaps or overlapping dates."""
    Window(start, end)
    windows = []
    cursor = start
    while cursor <= end:
        last = date(cursor.year, cursor.month, calendar.monthrange(cursor.year, cursor.month)[1])
        stop = min(last, end)
        windows.append(Window(cursor, stop))
        if stop == end:
            break
        cursor = stop + timedelta(days=1)
    return windows


def build_url(window: Window) -> str:
    return (
        ENDPOINT
        + "?"
        + urlencode(
            {
                "start_date": f"{window.start}T00:00",
                "end_date": f"{window.end}T23:59",
                "time_trunc": "day",
                "geo_trunc": "electric_system",
                "geo_limit": REGION,
                "geo_ids": "8741",
            }
        )
    )


def fetch(window: Window, *, opener=urlopen, sleep=time.sleep) -> bytes:
    """Retry transient failures at most three times; never retry ordinary 4xx errors."""
    request = Request(
        build_url(window),
        headers={"Accept": "application/json", "User-Agent": "spain-electricity-pipeline/0.1"},
    )
    for attempt in range(3):
        delay = 2**attempt
        try:
            with opener(request, timeout=30) as response:
                content_type = response.headers.get("Content-Type", "").lower()
                if "application/json" not in content_type:
                    raise ValueError(f"Expected a JSON response, got {content_type!r}")
                body = response.read(MAX_RESPONSE_BYTES + 1)
                if len(body) > MAX_RESPONSE_BYTES:
                    raise ValueError("Response exceeds the 10 MB safety limit")
                return body
        except HTTPError as error:
            if error.code not in RETRY_STATUSES or attempt == 2:
                raise
            retry_after = error.headers.get("Retry-After", "") if error.headers else ""
            if retry_after.isdigit():
                # Do not retry sooner than a provider-requested long backoff.
                if int(retry_after) > 30:
                    raise
                delay = max(delay, int(retry_after))
        except (URLError, TimeoutError):
            if attempt == 2:
                raise
        sleep(delay)
    raise RuntimeError("Unreachable retry state")


@dataclass(frozen=True)
class Retrieval:
    retrieval_id: str
    url: str
    region: str
    start_date: str
    end_date: str
    retrieved_at: str
    sha256: str
    raw_file: str


def archive(body: bytes, window: Window, root: Path) -> Retrieval:
    """Keep the exact response, including invalid payloads, for diagnosis."""
    root.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(body).hexdigest()
    raw_file = f"{digest}.json"
    path = root / raw_file
    try:
        with path.open("xb") as target:
            target.write(body)
    except FileExistsError:
        if path.read_bytes() != body:
            raise ValueError(f"Archived payload was modified: {path}") from None
    retrieval = Retrieval(
        retrieval_id=uuid.uuid4().hex,
        url=build_url(window),
        region=REGION,
        start_date=str(window.start),
        end_date=str(window.end),
        retrieved_at=datetime.now(UTC).isoformat(),
        sha256=digest,
        raw_file=raw_file,
    )
    manifest = root / f"{retrieval.retrieval_id}.manifest.json"
    with manifest.open("x", encoding="utf-8") as target:
        json.dump(asdict(retrieval), target, indent=2)
        target.write("\n")
    return retrieval
