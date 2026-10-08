# Q1–Q3 2024: validated historical extension

Source: **Red Eléctrica de España, REData**. Geography: **peninsular Spain**.

## Coverage and verification

Executed on **2026-10-08**. The verified warehouse now covers
**2024-01-01–2024-09-30**: **274 days**, **nine complete months** and **3,018
actual technology observations**. Q3 adds **92 days and 1,014 observations** to
the previously verified H1 snapshot.

All **9 SQL quality checks** passed. Every calendar date is present, technology
observations remain separate from the 274 published system totals, and no
duplicate source keys exist. No absent technology measurements were imputed.

All **127 active retrieval manifests** were replayed into a separate empty
warehouse with checksum verification. Generation rows, published totals and
acquisition metadata matched exactly; all three analytical CSV exports matched
byte for byte. The two-year history command still rejects this incomplete
2024–2025 dataset.

Maximum absolute daily reconciliation difference: **0.000000 MWh**.

## Quarterly comparison

Renewable shares use total renewable MWh divided by total generation MWh. Q3
contains 92 days, compared with 91 in Q2, so both total generation and the daily
average are shown.

| Period | Days | Generation (GWh) | GWh/day | Renewable share |
| --- | ---: | ---: | ---: | ---: |
| 2024-Q1 | 91 | 63,725.797 | 700.283 | 61.49% |
| 2024-Q2 | 91 | 59,453.905 | 653.340 | 65.26% |
| 2024-Q3 | 92 | 64,539.209 | 701.513 | 55.83% |
| Q1–Q3 2024 | 274 | 187,718.911 | 685.106 | 60.74% |

Q3 generation was **8.55% higher** than Q2, while generation per day was
**7.37% higher**. The energy-weighted renewable share was **9.43 percentage
points lower**. These are adjacent-quarter observations within 2024; they do
not establish recurring seasonality or identify weather, capacity or other
causal drivers.

## Complete Q3 months

| Month | Days | Generation (GWh) | Renewable share |
| --- | ---: | ---: | ---: |
| 2024-07 | 31 | 22,643.097 | 57.60% |
| 2024-08 | 31 | 21,712.832 | 54.82% |
| 2024-09 | 30 | 20,183.280 | 54.94% |

## Q3 technology observations

Provider names and renewable classifications are retained. Days observed count
actual rows, not assumed zero generation on absent dates. `Fuel + Gas` is
reported on only two Q3 days, so this table must not be interpreted as a fully
observed technology calendar.

| Source ID | Technology | Renewable | Days observed | Generation (GWh) |
| --- | --- | :---: | ---: | ---: |
| 1446 | Nuclear | No | 92 | 15,223.294068 |
| 1458 | Solar fotovoltaica | Yes | 92 | 15,138.893369 |
| 10291 | Eólica | Yes | 92 | 12,308.758081 |
| 1454 | Ciclo combinado | No | 92 | 7,975.948177 |
| 10288 | Hidráulica | Yes | 92 | 5,632.831991 |
| 10293 | Cogeneración | No | 92 | 4,189.759870 |
| 1459 | Solar térmica | Yes | 92 | 1,805.873518 |
| 10292 | Otras renovables | Yes | 92 | 963.958328 |
| 10289 | Carbón | No | 92 | 734.932224 |
| 10294 | Residuos no renovables | No | 92 | 380.690618 |
| 10295 | Residuos renovables | Yes | 92 | 184.268754 |
| 10290 | Fuel + Gas | No | 2 | 0.000002 |

## Sparse-series recovery

July passed monthly validation directly. The successful
[July source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-07-01T00%3A00&end_date=2024-07-31T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
was retrieved at 2026-10-08T17:21:37.123811+00:00. Its provider update is
2026-01-13T17:55:10.000+01:00 and its SHA-256 is
`31852e0d4915fb44eeb86f605bff4a2342b2c3ffed8c94f4f0fd4dbee8872ea7`.

The August and September monthly responses each reported `Fuel + Gas` (ID
`10290`) on only one date and therefore failed the existing complete-series
contract. Both responses were archived but never loaded:

| Window | Reported Fuel + Gas | Monthly observations | Published totals | Provider update | SHA-256 |
| --- | --- | ---: | ---: | --- | --- |
| 2024-08-01–2024-08-31 | 2024-08-14: 0.001 MWh | 342 | 31 | 2026-01-13T17:53:39.000+01:00 | `9a71e590751cd0078ce058a5df691cb3ba89ae03d85c8f7e2e10c803a3ed21bf` |
| 2024-09-01–2024-09-30 | 2024-09-18: 0.001 MWh | 331 | 30 | 2026-01-13T17:52:16.000+01:00 | `de7e095688a3551710c5c81ee4efb0c8226bb55e12ae7e4550ee0bf8f903ad49` |

Explicit daily requests then recovered both months. All reported technology
observations—including source IDs, names, classifications, energy and source
percentages—and every published total match the corresponding monthly payload
exactly. The two `Fuel + Gas` measurements are preserved; no rows were invented
for absent dates.

- [August source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-08-01T00%3A00&end_date=2024-08-31T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741);
  retrieved 2026-10-08T17:21:46.250332+00:00.
- [September source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-09-01T00%3A00&end_date=2024-09-30T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741);
  retrieved 2026-10-08T17:26:57.117280+00:00.

## Reproduce

Use a new database so these dates remain isolated from later loads:

```bash
python -m electricity_pipeline --start 2024-01-01 --end 2024-02-29 --database data/q1-q3-2024.duckdb --raw-dir data/q1-q3-raw --export-dir data/q1-q3-exports
python -m electricity_pipeline --start 2024-03-01 --end 2024-03-31 --request-window day --database data/q1-q3-2024.duckdb --raw-dir data/q1-q3-raw --export-dir data/q1-q3-exports
python -m electricity_pipeline --start 2024-04-01 --end 2024-05-31 --database data/q1-q3-2024.duckdb --raw-dir data/q1-q3-raw --export-dir data/q1-q3-exports
python -m electricity_pipeline --start 2024-06-01 --end 2024-06-30 --request-window day --database data/q1-q3-2024.duckdb --raw-dir data/q1-q3-raw --export-dir data/q1-q3-exports
python -m electricity_pipeline --start 2024-07-01 --end 2024-07-31 --database data/q1-q3-2024.duckdb --raw-dir data/q1-q3-raw --export-dir data/q1-q3-exports
python -m electricity_pipeline --start 2024-08-01 --end 2024-09-30 --request-window day --database data/q1-q3-2024.duckdb --raw-dir data/q1-q3-raw --export-dir data/q1-q3-exports
python -m electricity_pipeline.report --database data/q1-q3-2024.duckdb
```

A later API retrieval may contain revisions. Exact offline reproduction instead
replays the original manifests and their SHA-256-named payloads. Raw downloads,
manifests and databases are excluded from Git.

The Q3 snapshot comprises **62 active manifests**: one July monthly retrieval,
31 August daily retrievals and 30 September daily retrievals. Their original
acquisition timestamps span 2026-10-08T17:21:37.123811+00:00 through
2026-10-08T17:32:39.932065+00:00. Its evidence-set SHA-256 is
`c96e59eb2711b249c07ba2ffee6ddeb0b0fa035294404e3db21435852e98e757`.

This digest is calculated over successful Q3 records ordered by window start,
window end and retrieval ID, using lines of
`<retrieval_id> <payload_sha256>\n`. The full 127-manifest Q1–Q3 evidence-set
digest is `7f0cd4348ac6587fba24d478ec7f25025bb9ac1a721189e969f126c60fc318e5`.
Earlier source evidence remains in the [H1 report](baseline-2024-h1.md).

## Limits and next step

The remaining **October 2024–December 2025** history has not been validated in
this increment. Nine months do not establish a recurring annual pattern, and
this report does not complete the multi-year milestone. Generation is not
demand, prices or emissions; no such measures are inferred. Renewable status
follows the provider and source observations may be revised.

Independent educational analysis. Source data remain subject to
[Red Eléctrica's terms](https://www.ree.es/es/aviso-legal), not the code's MIT
license. See the [source contract](../docs/source-contract.md).
