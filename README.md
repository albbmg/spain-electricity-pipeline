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

Date limits are inclusive. Larger ranges are split into monthly requests. Today
and future dates are rejected. To update an existing range, run the same command
again against the same database. Each window is an independent transaction; a
failed later window leaves earlier valid windows intact. Only one writer should
use a database at a time.

Exports represent **all loaded dates in the database**, not just the most recent
request. A failed run does not refresh the export set: fix the error and rerun
before using earlier CSVs. The CSVs can be imported into Power BI; a finished
Power BI report is a later milestone, not part of this version.

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

The real-data baseline is a separate executed check, not a synthetic test result.
The included GitHub Actions workflow runs linting and tests on Python 3.12 and
3.13 after pushes and pull requests; its remote result must be checked after
publication.

## Model

- `generation`: daily technology observations, with source ID and retrieval lineage.
- `source_totals`: provider totals kept separately as reconciliation controls.
- `ingestion_runs`: request, checksum, timestamps and observation counts.
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
