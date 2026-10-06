# REData generation contract

## Request

`GET https://apidatos.ree.es/es/datos/generacion/estructura-generacion`

| Parameter | Value / rule |
| --- | --- |
| `start_date` | First requested local calendar date at `T00:00` |
| `end_date` | Last requested local calendar date at `T23:59` (inclusive) |
| `time_trunc` | `day` |
| `geo_trunc` | `electric_system` |
| `geo_limit` | `peninsular` |
| `geo_ids` | `8741` |

All three geography parameters are supplied: the API's default geography varies
between widgets. This dataset must not be described as the whole of Spain.
Requests are split at calendar-month boundaries to bound response size and allow
small, repeatable loads. No account or API key is required for this endpoint.

## Grain and types

One observation = **one local date × one source technology ID × peninsular system**.
The source values are daily energy in MWh, not instantaneous power in MW. GWh is
derived as MWh / 1,000. Original source percentages are retained for diagnostics;
analytical percentages are recalculated from energy amounts.

`attributes.type` defines `Renovable`, `No-Renovable` or `total`. The total is a
reconciliation control, never an additional technology. `composite: false` alone
does not identify a technology: the observed total also has this value.

Every returned technology and the total must have exactly one observation for each
requested date. Missing records are rejected, not filled with zeros. Zero generation
is valid. Negative/non-finite energy, unknown categories, duplicate keys, unexpected
dates, non-midnight timestamps and invalid timezone offsets fail validation.

Dates are interpreted in `Europe/Madrid`, preserving the daily labels across DST.
Validation compares the source offset with that timezone; converting to UTC and
then taking the date would shift winter midnight readings into the previous day.

Amounts use Python Decimal and DuckDB DECIMAL(24,6), rejecting excess precision.
Daily technology sums must equal the API total within the greater of **0.1 MWh**
and **one part per million of the total**. This accommodates rounding, not missing
material generation. Positive source totals and a complete date range are required.

## Updates and interpretation

Historical observations can change. Each retrieval records its URL, requested
window, UTC retrieval time, SHA-256 and source `last-update`. That field is a source
publication timestamp, not the observation date or a definitive/provisional flag.

A successful load replaces only its validated date window in one transaction. An
unchanged reload preserves the same analytical rows; a revised response replaces
old values and removes obsolete rows in that window. Other dates are preserved.
Multiple monthly requests commit independently: earlier valid windows remain if a
later request fails. The command exits unsuccessfully and can be rerun.

Recent or historical publication revisions are possible. Reconciliation validates
internal consistency, not the accuracy of the provider's measurements. The endpoint
does not establish household consumption, electricity costs or avoided emissions.
The provider states that estimated generation from self-consumption installations
is not included. Missing technologies are not inferred from a fixed global list;
the contract validates the series and total actually returned for each window.

## References

- [REData API](https://www.ree.es/en/datos/apidata), consulted 2026-10-05.
- [Generation structure and glossary](https://www.ree.es/es/datos/generacion/estructura-generacion), consulted 2026-10-05.
- [Provider terms](https://www.ree.es/es/aviso-legal), consulted 2026-10-05.

The informational-use attribution conditions are separate from the code license.
Source names, units and dates must remain visible in any published results.

## Offline replay contract

`--replay-manifest` accepts one manifest produced by this pipeline and reads its
sibling `<sha256>.json` payload. It validates the exact retrieval fields and types,
canonical request URL, peninsular region, within-month date window, UTC acquisition
time, filename and SHA-256 before opening the warehouse. Duplicate JSON keys,
missing payloads, symbolic-link payloads, path traversal and inconsistent metadata
are rejected. Files are size-bounded; the payload then passes the same source-data
validation as a live response. No network call or archive rewrite is performed.

The original acquisition remains in `ingestion_runs`. A separate `replay_runs`
record stores the actual replay time and references that acquisition. Repeated
replays may reuse the original retrieval record only when **all recorded metadata
agree**; conflicts fail. Replay audit insertion and analytical window replacement
commit together, or both roll back. A fresh replay database can therefore reproduce
the original source lineage and CSV values without representing replay as a download.

Older warehouses acquire only the new audit table; no existing timestamps or
observations are migrated or deleted during schema setup. Replay uses the same
explicit window-replacement semantics as live loading. An older archive can replace
a newer overlapping window, so use a separate database for historical reconstruction.
The archive checksum checks payload integrity relative to the manifest, not source
authenticity. Preserve the original manifest and payload together as trusted evidence.
