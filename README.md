# Spain Electricity Pipeline

A reproducible data pipeline for understanding the **generation mix of the Spanish
peninsular electricity system**, using the public Red Eléctrica REData API.

Historical daily generation is retrieved, checked against the published total and
loaded into an analytical database. Raw responses retain their checksum and retrieval
metadata. Repeated loads replace their date window without duplicating observations.

**Verified baseline:** Q1 2025, **90 days**, **990 technology observations**,
**11 technologies**, **41 passing tests** and **9 passing SQL quality checks**.
The complete pipeline was run against the live API on 2026-10-05.

The baseline contains **66,409.067 GWh** of generation, of which **59.05%** is renewable
under the provider's classification. Read the [reproducible baseline](reports/baseline-2025-q1.md)
for monthly results, source update dates and limitations.

## Questions

- How does renewable generation's share change across days and months?
- Which technologies account for the changes in the generation mix?
- Can the reported totals be reconciled with their underlying observations?
- How can a revised API response replace an earlier load without duplicating data?

## Approach

**REData REST API → immutable raw JSON → validation → DuckDB → SQL marts → CSV**

Python handles acquisition and contracts. DuckDB keeps the analytical model runnable
locally without a server or cloud account. Versioned SQL owns the metric definitions.

Scope is deliberately explicit: **peninsular Spain**, daily generation, historical
closed dates. Generation is not electricity demand, prices, customer bills or carbon
emissions. The project does not infer those measures from the generation mix.

See [the source contract](docs/source-contract.md) and [the roadmap](docs/roadmap.md).

## Run locally

Python **3.12+** is required; local verification used Python **3.12.14**.
No API key, paid cloud service or database server is needed.

From the repository root, create and activate an environment:

```powershell
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

Then install and run the Q1 baseline:

```bash
python -m pip install -e ".[dev]"
python -m electricity_pipeline --start 2025-01-01 --end 2025-03-31
python -m electricity_pipeline.report
```

The command creates a local `data/electricity.duckdb`, raw JSON and retrieval
manifests under `data/raw/`, and these UTF-8 CSVs under `data/exports/`:

| Export | Grain | Main use |
| --- | --- | --- |
| `daily_mix.csv` | System × day | Generation, renewable share, source reconciliation and lineage |
| `monthly_mix.csv` | System × month | Energy-weighted monthly shares and explicit completeness |
| `monthly_technology.csv` | System × month × technology attributes | Contribution by generation technology |

Date limits are inclusive. Larger ranges are split into monthly requests by default. Today
and future dates are rejected. To update an existing range, run the same command
again against the same database. Each window is an independent transaction; a
failed later window leaves earlier valid windows intact. Only one writer should
use a database at a time.

For a source window that needs investigation at a narrower request size, opt into
one API request per day:

```bash
python -m electricity_pipeline --start 2024-03-01 --end 2024-03-31 --request-window day --database data/march-daily.duckdb --raw-dir data/march-raw --export-dir data/march-exports
```

`--request-window month` is the default; `day` changes the request boundaries, not
the daily measurement grain or validation rules. Daily mode makes one request per
selected date, each with its own archive, transaction and revision audit. It is
explicit, with no automatic fallback or extra requests after a monthly failure.
Replay follows the archived window and rejects `--request-window`.

Daily queries can return different technology sets. Store only what each response
actually supplies: an absent series is not an observed zero, and no rows are invented
to fill a technology calendar. Returned series must still cover their request and
reconcile with the published total. `monthly_technology.days_observed` makes sparse
technology coverage visible. Use `daily_mix`/`monthly_mix` for system-wide totals.

Exports represent **all loaded dates in the database**, not just the most recent
request. A failed run does not refresh the export set: fix the error and rerun
before using earlier CSVs. The CSVs can be imported into Power BI; a finished
Power BI report is an optional future extension, not part of this version.

## Offline interactive dashboard

Build a self-contained HTML report from a validated historical warehouse:

```bash
python -m electricity_pipeline.dashboard --database data/history.duckdb --start-year 2024 --end-year 2025 --output data/dashboard.html
```

Open `data/dashboard.html` in a browser. No server, API request, external script or
Power BI installation is needed. JavaScript must be enabled. Select a year or the
entire period to explore generation, energy-weighted renewable share, daily average
and monthly generation bars. Expand the monthly table for exact values and the
source evidence for acquisition timestamps, provider update dates and checksums.

The technology table adds month and renewable-classification filters, source IDs,
observed-day coverage and each contribution's share of full-month generation.
Those filters affect only this table, not the overview or selected-period evidence.
Missing technology days are not filled with zeros; measured zeros remain visible.
Changes in a source ID's name or classification are shown as separate monthly rows.

The year-on-year panel compares a chosen month with the same month one year earlier
within the exported history. It shows both months' generation, calendar-day counts,
daily averages and renewable shares, plus percentage changes and share changes in
percentage points. Its evidence is scoped to those two months; the first exported
year has no comparison, even if older data exist elsewhere in the warehouse.

The command requires at least two complete past years and runs the same quality
and completeness checks as the historical report. It opens the warehouse read-only
and replaces the HTML atomically after successful validation; failures preserve an
existing report. The output directory must already exist. Published totals remain
separate controls. KPI arithmetic uses Python Decimal; browser floating-point
numbers only set chart widths. Chart scales adjust to the selected period.

The report includes derived aggregates and source metadata, not raw downloads or
the database. Retain its attribution and provider terms when sharing it. An HTML
snapshot does not refresh itself: regenerate it after validated data updates.
The web dashboard is the active presentation path; Power BI remains optional.
See the [executed dashboard checks](reports/dashboard-overview-verification.md).
The [technology verification](reports/dashboard-technology-verification.md) records
SQL reconciliation, sparse-series cases and offline desktop/mobile filter checks.
See also the [comparable-period verification](reports/dashboard-comparison-verification.md).

## Rebuild from an archive without the API

Keep each original `*.manifest.json` beside its SHA-256-named JSON payload. Replace
`RETRIEVAL_ID` below with the name of an existing manifest:

```bash
python -m electricity_pipeline --replay-manifest data/raw/RETRIEVAL_ID.manifest.json --database data/replayed.duckdb --export-dir data/replayed-exports
```

The command reads one archived window, verifies the manifest and payload checksum,
applies the normal source-validation rules and loads the reporting model without
an API request. It does not write to the archive. Run it once per manifest to rebuild
several windows; `--start` and `--end` cannot be combined with replay mode, and
`--raw-dir` is only used by live acquisition.

The original retrieval ID, URL, checksum and `retrieved_at` remain unchanged.
`replay_runs` records a separate UTC `replayed_at` for each successful replay,
including repeat executions. Replaying the same manifest does not duplicate
analytical rows or invent a new source download. Conflicting metadata for an
existing retrieval ID fail and roll back the window replacement.

Use a separate database as above to reconstruct an older snapshot: replay into an
existing database **replaces its overlapping dates**, even if that database contains
newer source revisions. Other windows are retained. The checksum detects changes
to a payload relative to its manifest; it does not authenticate a manifest that has
also been edited. Keep both files from a trusted original acquisition.

The three original Q1 2025 manifests were replayed on 2026-10-06 without API access.
All **990 observations**, source totals, retrieval metadata and reporting views
matched the original warehouse; all three CSV exports matched byte for byte.

## Data quality and tests

```bash
ruff check .
ruff format --check .
pytest -q
```

The tests use **explicitly synthetic source examples** and real temporary DuckDB
databases. They require no network access. They cover duplicate and missing
observations, DST, invalid numbers, bounded retries, total reconciliation,
transaction rollback, repeat loads, revised partitions and weighted percentages.
The current suite contains **119 passing tests**, including offline replay, manifest
integrity, timestamp preservation, revision counts, audit rollback and compatibility
with existing warehouses. Historical-report tests also cover leap years, weighted
shares, matching calendar months, selected-period lineage and rejection of gaps.
Dashboard tests cover weighted indicators, isolated published totals, safe embedded
JSON, deterministic output, read-only access and preservation of a report on failure.
Technology cases independently aggregate source rows with SQL, covering sparse
observations, recorded zeros, absent series and changes in names/classifications.
Monthly comparisons are checked against the generated historical report, including
leap-year daily averages, negative/zero changes, unrounded percentage-point arithmetic
and currently referenced source evidence for both months.

The real-data baseline is a separate executed check, not a synthetic test result.
The included GitHub Actions workflow runs linting and tests on Python 3.12 and
3.13 after pushes and pull requests; its remote result must be checked after
publication.

## Historical comparisons

The historical report command reads an existing warehouse without changing it:

```bash
python -m electricity_pipeline.history --database data/history.duckdb --start-year 2024 --end-year 2025
```

It requires at least two complete past calendar years, checks every selected date,
and produces annual, calendar-quarter and monthly summaries in Markdown. Monthly
YoY comparisons use the same calendar month of the preceding year. Energy-weighted
renewable shares and percentage-point changes are shown alongside generation totals
and daily averages, so leap-year differences remain visible. Only the selected years
and their currently referenced source evidence appear in the report.

**Real-data status:** on 2026-10-13, the validated historical warehouse covers
**2024-01-01–2025-12-31: 731 consecutive days, 24 complete months and 8,214
technology observations**. Q4 2025 completed the two-year selection without
changing the previously verified history through Q3.

All 231 active source manifests reproduce the combined warehouse exactly; source
tables, all three CSV exports and the generated history report match byte for byte.
The Q4 audit records 1,104 added technology observations and 92 added published
totals, with no changes or removals.

The guarded [2024–2025 historical report](reports/history-2024-2025.md) now runs
successfully. Generation was **248,642.883 GWh** in 2024 and **258,120.232 GWh**
in 2025; the daily average changed **+4.10%** and renewable share changed from
**58.96%** to **57.54%**. See the
[Q4 completion evidence](reports/history-2025-q4-completion.md) and the
[Q3 extension evidence](reports/history-2025-q3-extension.md). These are
descriptive results for the selected years, not causal findings or a long-term trend.

## Audit source revisions

Each successful live load or offline replay prints a `revision` JSON summary and
stores it in `revision_runs`. Counts distinguish added, changed, removed and unchanged
rows within the requested window. Technology observations and published totals are
counted separately. A first load into an empty window counts as additions; a repeat
with identical values counts as unchanged, even when retrieval or publication dates differ.

For technology rows, a change means a different name, renewable classification, MWh
value or stored source percentage for the same date and technology ID. The audit
compares the values stored in DuckDB, including nullable DOUBLE source percentages;
MWh comparisons use exact decimals. Totals compare their MWh value by date.
Other dates are not included in the comparison or changed by the load.

Inspect recent loads with this SQL against the local warehouse:

```sql
SELECT r.loaded_at, r.mode, i.start_date, i.end_date,
       r.generation_added, r.generation_changed, r.generation_removed,
       r.generation_unchanged, r.totals_added, r.totals_changed,
       r.totals_removed, r.totals_unchanged,
       r.previous_retrieval_ids, r.retrieval_id, i.sha256
FROM revision_runs AS r
JOIN ingestion_runs AS i USING (retrieval_id)
ORDER BY r.loaded_at DESC, r.revision_id;
```

Each event records its actual UTC load time, live/replay mode, incoming retrieval
and all prior retrieval IDs found in that window. Original retrieval metadata and
raw archives remain the source evidence. Counts describe changes to the local
warehouse, not necessarily new provider corrections: replaying an older archive can
also change values. This is a summary audit, not a row-level version history.

Audit and data writes share one transaction: failed loads leave neither partial
replacement data nor a successful audit event. Existing warehouses acquire the table
automatically. Audit history begins with the next successful load; earlier events
are not reconstructed or assigned fabricated timestamps.

Verification on 2026-10-06 replayed the three original Q1 2025 archives into a copy
of the existing warehouse: the audit recorded **990 unchanged observations** and
**90 unchanged totals**, with no additions, changes or removals. All three analytical
CSV exports remained byte-identical to the baseline.

## Model

- `generation`: daily technology observations, with source ID and retrieval lineage.
- `source_totals`: provider totals kept separately as reconciliation controls.
- `ingestion_runs`: request, checksum, timestamps and observation counts.
- `replay_runs`: successful offline executions linked to their original retrieval;
  the table is added automatically when opening an older warehouse.
- `revision_runs`: per-load comparison counts, execution time and previous retrieval IDs.
- `daily_mix`, `monthly_mix`, `monthly_technology`: reporting views defined in
  [versioned SQL](src/electricity_pipeline/sql/).

Raw payloads are retained by SHA-256. Existing analytical windows are replaced
only after their new response satisfies the documented contract. Renewable status
comes from the source, and monthly shares are calculated as total renewable energy
divided by total energy, not the average of daily percentages.

## Source and attribution

Source: **Red Eléctrica de España, REData**.

- [API documentation](https://www.ree.es/en/datos/apidata)
- [Generation methodology and glossary](https://www.ree.es/es/datos/generacion/estructura-generacion)
- [Source terms](https://www.ree.es/es/aviso-legal)

This is an independent educational analysis. REData data remain subject to the
provider's terms; they are not relicensed by this repository. Raw downloads and the
local database are excluded from Git. Published analytical results must retain
source attribution and the source-update and retrieval dates. There is no affiliation
with Red Eléctrica.

Project code is available under the [MIT License](LICENSE).
