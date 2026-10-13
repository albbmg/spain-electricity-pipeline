# Q4 2025: verified completion of the two-year history

Source: **Red Eléctrica de España, REData**. Geography: **peninsular Spain**.

## Scope

Executed on **2026-10-13**. Three monthly API responses for October–December
2025 passed the existing source contract directly, were archived with their
checksums and were loaded into a fresh reconstruction of the verified history
through Q3 2025.

The resulting coverage is **2024-01-01–2025-12-31**: **731 consecutive days**,
**24 complete months**, **8,214 actual technology observations** and **731
published system totals**. Source totals remain separate from technology rows.

## Integration verification

- The pre-existing **7,110 technology observations**, **639 published totals**
  and **228 acquisition records** through 2025-09-30 remained exactly unchanged.
- Q4 2025 added **1,104 technology observations** and **92 published totals**.
  The revision audit recorded only additions: no changed, removed or unchanged
  rows in those previously empty dates.
- All **231 active manifests** were checksum-verified and replayed into another
  empty warehouse. Generation rows, published totals and acquisition metadata
  matched the live-integrated warehouse exactly.
- All three replayed CSV exports matched the live-integrated exports byte for
  byte. All **9 SQL quality checks** passed, with no missing calendar dates or
  duplicate source keys. Maximum daily reconciliation difference was
  **0.000000 MWh**.
- The guarded history command accepted 2024–2025 and generated the complete
  [two-year report](history-2024-2025.md). Running it against the offline replay
  produced that report byte for byte.

## Q4 descriptive check

Both quarters contain 92 days. Shares are energy-weighted and the comparison
does not establish causes.

| Period | Days | Generation (GWh) | GWh/day | Renewable generation (GWh) | Renewable share |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2024-Q4 | 92 | 60,923.973 | 662.217 | 32,579.238 | 53.48% |
| 2025-Q4 | 92 | 64,380.824 | 699.792 | 34,693.729 | 53.89% |
| Observed change | — | +5.67% | +5.67% | +6.49% | +0.41 pp |

Across the complete years, generation increased **3.81%** from
**248,642.883 GWh** in 2024 to **258,120.232 GWh** in 2025. The daily average
increased **4.10%** after accounting for the 2024 leap day. Renewable share was
**58.96%** in 2024 and **57.54%** in 2025, a **-1.42 percentage-point** change.
These are observations for these two years, not a long-term trend.

## Q4 source evidence

These are original acquisition and provider publication times, not replay times:

| Window | Retrieval ID | Provider update | Retrieved at (UTC) | SHA-256 |
| --- | --- | --- | --- | --- |
| [2025-10-01–2025-10-31](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2025-10-01T00%3A00&end_date=2025-10-31T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741) | `e3581c286075412b94294a7a63efae9a` | 2026-05-12T14:54:07.000+02:00 | 2026-10-13T17:09:27.870509+00:00 | `4bc0be58d8836b0de86446eb99183171eddf7bb410007022c12806f91fa10706` |
| [2025-11-01–2025-11-30](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2025-11-01T00%3A00&end_date=2025-11-30T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741) | `f62b18f9a4c540bc94a9ba80ff7cf32c` | 2026-05-12T00:51:25.000+02:00 | 2026-10-13T17:09:37.030118+00:00 | `865ff69d408472dffef76a217b094b496f3e6c81d7cc9ef4fbb7c8acc3d25f16` |
| [2025-12-01–2025-12-31](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2025-12-01T00%3A00&end_date=2025-12-31T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741) | `b12ff80740c54e9eb443ed8a6e7d16fb` | 2026-05-12T00:50:08.000+02:00 | 2026-10-13T17:09:53.226674+00:00 | `e494059843de843c855503b8841d16126df3897d8e253b584341abfb96990041` |

The Q4 evidence-set SHA-256 is
`b54e5ed443f197ce598313c44b784650edad33d0a49c7e6c0d4debc430050826`.
The combined 231-manifest evidence-set SHA-256 is
`926269982946fef73b77717245bafaebcc37fb38bf0c1dfb7d99ac398acbb098`.
Each digest uses records ordered by window start, window end and retrieval ID,
with lines of `<retrieval_id> <payload_sha256>\n`.

## Reproduce the completion

First reconstruct the history through Q3 2025 as documented in the
[Q3 extension report](history-2025-q3-extension.md). Then replay the three
trusted Q4 archives into that database and render the history report:

```bash
python -m electricity_pipeline --replay-manifest data/q4-2025-raw/e3581c286075412b94294a7a63efae9a.manifest.json --database data/history.duckdb --export-dir data/history-exports
python -m electricity_pipeline --replay-manifest data/q4-2025-raw/f62b18f9a4c540bc94a9ba80ff7cf32c.manifest.json --database data/history.duckdb --export-dir data/history-exports
python -m electricity_pipeline --replay-manifest data/q4-2025-raw/b12ff80740c54e9eb443ed8a6e7d16fb.manifest.json --database data/history.duckdb --export-dir data/history-exports
python -m electricity_pipeline.history --database data/history.duckdb --start-year 2024 --end-year 2025
```

The manifests and their SHA-256-named payloads must remain together. Raw
downloads, manifests and databases are excluded from Git.

## Limits and next step

The historical-analysis milestone is complete for the selected two years. The
report is descriptive, does not establish causal drivers and may change if the
provider revises the source observations.

The remaining roadmap item is an implemented and verified Power BI report. No
PBIX is claimed here: a data model or written specification alone would not
complete that milestone.

Generation is not demand, prices or emissions; no such measures are inferred.
Renewable status follows the provider.

Independent educational analysis. Source data remain subject to
[Red Eléctrica's terms](https://www.ree.es/es/aviso-legal), not the code's MIT
license. See the [source contract](../docs/source-contract.md).
