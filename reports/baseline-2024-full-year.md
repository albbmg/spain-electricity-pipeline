# 2024: validated full-year generation baseline

Source: **Red Eléctrica de España, REData**. Geography: **peninsular Spain**.

## Coverage and verification

Executed on **2026-10-09**. The verified warehouse covers the complete leap year
**2024-01-01–2024-12-31**: **366 days**, **12 complete months** and **4,030
actual technology observations**. Q4 adds **92 days and 1,012 observations** to
the previously verified Q1–Q3 snapshot.

All **9 SQL quality checks** passed. Every calendar date, including 2024-02-29,
is present. Technology observations remain separate from the 366 published
system totals, no duplicate source keys exist, and no absent technology
measurements were imputed.

All **130 active retrieval manifests** were replayed into a separate empty
warehouse with checksum verification. Generation rows, published totals and
acquisition metadata matched exactly; all three analytical CSV exports matched
byte for byte. The two-year history command still rejects the incomplete
2024–2025 selection.

Maximum absolute daily reconciliation difference: **0.000000 MWh**.

## Full-year result

The 2024 snapshot contains **248,642.883 GWh** of generation, of which
**58.96%** is renewable under the provider's classification. The daily average
is **679.352 GWh**.

| Period | Days | Generation (GWh) | GWh/day | Renewable share |
| --- | ---: | ---: | ---: | ---: |
| 2024-Q1 | 91 | 63,725.797 | 700.283 | 61.49% |
| 2024-Q2 | 91 | 59,453.905 | 653.340 | 65.26% |
| 2024-Q3 | 92 | 64,539.209 | 701.513 | 55.83% |
| 2024-Q4 | 92 | 60,923.973 | 662.217 | 53.48% |
| 2024 | 366 | 248,642.883 | 679.352 | 58.96% |

Q4 generation was **5.60% lower** than Q3. Both quarters contain 92 days, so
the total and daily-average relative changes are identical. The energy-weighted
renewable share was **2.36 percentage points lower**. These adjacent-quarter
observations do not establish recurring seasonality or identify weather,
capacity or other causal drivers.

## Complete monthly periods

| Month | Days | Generation (GWh) | Renewable share |
| --- | ---: | ---: | ---: |
| 2024-01 | 31 | 22,019.078 | 54.30% |
| 2024-02 | 29 | 20,758.287 | 62.31% |
| 2024-03 | 31 | 20,948.432 | 68.22% |
| 2024-04 | 30 | 19,656.570 | 68.22% |
| 2024-05 | 31 | 19,758.288 | 66.19% |
| 2024-06 | 30 | 20,039.047 | 61.45% |
| 2024-07 | 31 | 22,643.097 | 57.60% |
| 2024-08 | 31 | 21,712.832 | 54.82% |
| 2024-09 | 30 | 20,183.280 | 54.94% |
| 2024-10 | 31 | 20,244.347 | 57.71% |
| 2024-11 | 30 | 19,360.429 | 53.07% |
| 2024-12 | 31 | 21,319.197 | 49.82% |

November has the lowest generation total in this observed year; July has the
highest. March and April have the highest renewable shares after rounding to
two decimals, while December has the lowest. One year alone does not establish
a recurring seasonal pattern.

## Annual technology observations

Provider names and renewable classifications are retained. Days observed count
actual source rows, not assumed zero generation on absent dates. In particular,
`Fuel + Gas` is reported on only four days.

| Source ID | Technology | Renewable | Days observed | Generation (GWh) |
| --- | --- | :---: | ---: | ---: |
| 10291 | Eólica | Yes | 366 | 59,503.767301 |
| 1446 | Nuclear | No | 366 | 52,390.802937 |
| 1458 | Solar fotovoltaica | Yes | 366 | 43,685.524330 |
| 10288 | Hidráulica | Yes | 366 | 34,946.429942 |
| 1454 | Ciclo combinado | No | 366 | 29,106.723922 |
| 10293 | Cogeneración | No | 366 | 16,381.279962 |
| 1459 | Solar térmica | Yes | 366 | 4,127.370569 |
| 10292 | Otras renovables | Yes | 366 | 3,680.511731 |
| 10289 | Carbón | No | 366 | 2,972.389074 |
| 10294 | Residuos no renovables | No | 366 | 1,194.495108 |
| 10295 | Residuos renovables | Yes | 366 | 653.588164 |
| 10290 | Fuel + Gas | No | 4 | 0.000004 |

## Q4 source evidence

All three Q4 monthly responses passed the normal completeness, precision,
timezone and total-reconciliation rules directly.

| Window | Observations | Provider update | Retrieved at (UTC) | SHA-256 |
| --- | ---: | --- | --- | --- |
| [October](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-10-01T00%3A00&end_date=2024-10-31T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741) | 341 | 2026-01-13T19:24:57.000+01:00 | 2026-10-09T17:11:42.890619+00:00 | `c2b2255d2176abe24343772172bc9473c089d06222f3b1d606864a9dea9a01ae` |
| [November](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-11-01T00%3A00&end_date=2024-11-30T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741) | 330 | 2026-01-13T19:23:38.000+01:00 | 2026-10-09T17:11:50.177488+00:00 | `c60e29748ce4959d2b115ce5a7503fdafb96c75a9069dc4193cc9d7ee3a76ae4` |
| [December](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-12-01T00%3A00&end_date=2024-12-31T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741) | 341 | 2026-01-13T19:22:20.000+01:00 | 2026-10-09T17:11:57.833647+00:00 | `8f32f1dd5b9fb1ef46ce369d96bab3632dbbcdc6a02caa5dd824fe0cb85efcd7` |

## Reproduce

Use a new database so the annual snapshot remains isolated from later loads:

```bash
python -m electricity_pipeline --start 2024-01-01 --end 2024-02-29 --database data/2024.duckdb --raw-dir data/2024-raw --export-dir data/2024-exports
python -m electricity_pipeline --start 2024-03-01 --end 2024-03-31 --request-window day --database data/2024.duckdb --raw-dir data/2024-raw --export-dir data/2024-exports
python -m electricity_pipeline --start 2024-04-01 --end 2024-05-31 --database data/2024.duckdb --raw-dir data/2024-raw --export-dir data/2024-exports
python -m electricity_pipeline --start 2024-06-01 --end 2024-06-30 --request-window day --database data/2024.duckdb --raw-dir data/2024-raw --export-dir data/2024-exports
python -m electricity_pipeline --start 2024-07-01 --end 2024-07-31 --database data/2024.duckdb --raw-dir data/2024-raw --export-dir data/2024-exports
python -m electricity_pipeline --start 2024-08-01 --end 2024-09-30 --request-window day --database data/2024.duckdb --raw-dir data/2024-raw --export-dir data/2024-exports
python -m electricity_pipeline --start 2024-10-01 --end 2024-12-31 --database data/2024.duckdb --raw-dir data/2024-raw --export-dir data/2024-exports
python -m electricity_pipeline.report --database data/2024.duckdb
```

A later API retrieval may contain revisions. Exact offline reproduction instead
replays the original manifests and their SHA-256-named payloads. Raw downloads,
manifests and databases are excluded from Git.

The Q4 snapshot comprises **three active monthly manifests**. Its evidence-set
SHA-256 is
`8b9f2eee360a9994a36e4aad61914f20b8621d542647b9cf8afc3022e990f5c8`.
The full 130-manifest 2024 evidence-set SHA-256 is
`416eeec829fc8ddc6765da59e495f4630c95f638acc6ceec2efee0098c2ef1e3`.
Each digest uses records ordered by window start, window end and retrieval ID,
with lines of `<retrieval_id> <payload_sha256>\n`. Earlier source evidence
remains in the [Q1–Q3 report](baseline-2024-q1-q3.md).

## Limits and next step

This is one complete calendar year, not a multi-year trend. The validated Q1
2025 baseline exists separately, but 2025 has not yet been assembled as a
complete year in this historical warehouse. The next step is to replay that
verified Q1 snapshot here, then acquire and validate April–December 2025.

Generation is not demand, prices or emissions; no such measures are inferred.
Renewable status follows the provider and source observations may be revised.

Independent educational analysis. Source data remain subject to
[Red Eléctrica's terms](https://www.ree.es/es/aviso-legal), not the code's MIT
license. See the [source contract](../docs/source-contract.md).
