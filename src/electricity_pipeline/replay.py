"""Read and validate an archived response without network access or archive writes."""

import hashlib
import json
import re
from dataclasses import fields
from datetime import date, timedelta
from pathlib import Path

from electricity_pipeline.source import MAX_RESPONSE_BYTES, REGION, Retrieval, Window, build_url
from electricity_pipeline.validation import (
    Batch,
    aware_timestamp,
    parse,
    reject_constant,
    reject_duplicate_keys,
)


def read_bounded(path: Path, limit: int) -> bytes:
    if not path.is_file():
        raise ValueError(f"Archive file is missing or not a regular file: {path.name}")
    with path.open("rb") as source:
        body = source.read(limit + 1)
    if len(body) > limit:
        raise ValueError(f"Archive file exceeds its {limit}-byte limit: {path.name}")
    return body


def read_manifest(path: Path) -> tuple[Batch, Retrieval]:
    """Verify a pipeline-generated manifest and its sibling SHA-256-named payload."""
    metadata = json.loads(
        read_bounded(path, 64_000),
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_constant,
    )
    expected = {field.name for field in fields(Retrieval)}
    if not isinstance(metadata, dict) or set(metadata) != expected:
        raise ValueError("Manifest must contain exactly the original retrieval fields")
    if any(not isinstance(value, str) or not value for value in metadata.values()):
        raise ValueError("Manifest fields must be non-empty strings")
    retrieval = Retrieval(**metadata)
    if not re.fullmatch(r"[0-9a-f]{32}", retrieval.retrieval_id):
        raise ValueError("Invalid manifest retrieval ID")
    if not re.fullmatch(r"[0-9a-f]{64}", retrieval.sha256):
        raise ValueError("Invalid manifest SHA-256")
    if retrieval.raw_file != f"{retrieval.sha256}.json":
        raise ValueError("Payload must use its SHA-256 filename beside the manifest")
    window = Window(
        date.fromisoformat(retrieval.start_date), date.fromisoformat(retrieval.end_date)
    )
    if (retrieval.start_date, retrieval.end_date) != (str(window.start), str(window.end)):
        raise ValueError("Manifest dates must use YYYY-MM-DD")
    if (window.start.year, window.start.month) != (window.end.year, window.end.month):
        raise ValueError("A retrieval window must stay within one calendar month")
    if retrieval.region != REGION or retrieval.url != build_url(window):
        raise ValueError("Manifest request does not match the peninsular daily-generation contract")
    if aware_timestamp(retrieval.retrieved_at, "retrieved_at").utcoffset() != timedelta(0):
        raise ValueError("Manifest retrieval time must be UTC")

    raw_path = path.parent / retrieval.raw_file
    if raw_path.is_symlink():
        raise ValueError("Archived payload must be a regular sibling file, not a symbolic link")
    body = read_bounded(raw_path, MAX_RESPONSE_BYTES)
    if hashlib.sha256(body).hexdigest() != retrieval.sha256:
        raise ValueError("Archived payload SHA-256 mismatch")
    # Integrity alone is insufficient: apply the same data contract as live ingestion.
    return parse(body, window), retrieval
