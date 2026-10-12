# Q3 2025: verified daily recovery and history extension

Source: **Red Eléctrica de España, REData**. Geography: **peninsular Spain**.

## Coverage and verification

Executed on **2026-10-12**. The verified warehouse now covers
**2024-01-01–2025-09-30**: **639 consecutive days**, **21 complete months**,
**7,110 actual technology observations** and **639 published system totals**.
Q3 2025 adds **92 days and 1,089 observations** to the previously verified
history through June 2025.

All **9 SQL quality checks** passed. Every calendar date is present, technology
observations remain separate from published totals, and no duplicate source keys
exist. No absent technology measurements were imputed.

All **228 active retrieval manifests** were checksum-verified and replayed into
a separate empty warehouse. Generation rows, published totals and acquisition
metadata matched exactly; all three analytical CSV exports matched byte for byte.
The pre-existing 6,021 observations, 547 totals and 136 acquisition records
through 2025-06-30 also remained exactly unchanged.

The revision audit records 1,089 technology additions and 92 published-total
additions for Q3, with no changed, removed or unchanged rows in those previously
empty dates. The guarded two-year history command still rejects the selection
because October–December 2025 are absent.

Maximum absolute daily reconciliation difference in Q3: **0.000000 MWh**.

## Same-quarter comparison

Renewable shares use total renewable MWh divided by total generation MWh. Both
quarters contain 92 days, so total and per-day generation changes are equal.

| Period | Days | Generation (GWh) | GWh/day | Renewable generation (GWh) | Renewable share |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2024-Q3 | 92 | 64,539.209 | 701.513 | 36,034.584 | 55.83% |
| 2025-Q3 | 92 | 66,496.058 | 722.783 | 36,901.604 | 55.49% |
| Observed change | — | +3.03% | +3.03% | +2.41% | -0.34 pp |

This is a like-calendar-quarter descriptive check, not the complete guarded
two-year report and not evidence of a cause.

## Complete Q3 months

| Month | Days | Generation (GWh) | Renewable share |
| --- | ---: | ---: | ---: |
| 2025-07 | 31 | 23,845.279 | 57.03% |
| 2025-08 | 31 | 22,145.819 | 54.28% |
| 2025-09 | 30 | 20,504.959 | 55.03% |

## Q3 technology observations

Provider names and renewable classifications are retained. Days observed count
actual rows, not assumed zero generation on absent dates.

| Source ID | Technology | Renewable | Days observed | Generation (GWh) |
| --- | --- | :---: | ---: | ---: |
| 1458 | Solar fotovoltaica | Yes | 92 | 16,883.480808 |
| 1446 | Nuclear | No | 92 | 14,696.038337 |
| 10291 | Eólica | Yes | 92 | 11,990.459344 |
| 1454 | Ciclo combinado | No | 92 | 10,268.532720 |
| 10288 | Hidráulica | Yes | 92 | 5,307.124491 |
| 10293 | Cogeneración | No | 92 | 3,812.556719 |
| 1459 | Solar térmica | Yes | 92 | 1,545.041613 |
| 10292 | Otras renovables | Yes | 92 | 1,019.199804 |
| 1451 | Turbina de vapor | No | 76 | 457.942208 |
| 10294 | Residuos no renovables | No | 92 | 246.205704 |
| 10295 | Residuos renovables | Yes | 92 | 156.297922 |
| 10289 | Carbón | No | 92 | 113.177877 |
| 10290 | Fuel + Gas | No | 1 | 0.000001 |

`Turbina de vapor` is absent on July 1–14 and August 16–17. `Fuel + Gas`
appears only on September 16 at 0.001 MWh. These observations are preserved as
published; no zero rows were invented for absent dates.

## Sparse-series recovery

The initial [July monthly request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2025-07-01T00%3A00&end_date=2025-07-31T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
reported `Turbina de vapor` only from July 15 through July 31. It therefore
failed the existing complete-series contract, was archived and was never loaded:

| Retrieval ID | Technology observations | Published totals | Provider update | Retrieved at (UTC) | SHA-256 |
| --- | ---: | ---: | --- | --- | --- |
| `f4896e33b9c84637a29301bae02092ae` | 358 | 31 | 2026-06-04T16:19:07.000+02:00 | 2026-10-12T17:42:07.377296+00:00 | `c912f44c03045cb97e765c586584bd26d65b6037e4b97713f6c918a226e59a23` |

The multi-month command stopped at that first failed window, so it did not
request monthly August or September responses. An explicit daily request then
recovered all 92 Q3 dates under the unchanged source contract. All 358 July
technology observations—including IDs, names, classifications, energy and source
percentages—and all 31 published totals match the archived monthly payload exactly.

The successful daily evidence is summarized below. Acquisition times and source
publication times are original evidence, not replay timestamps.

| Month | Daily manifests | Provider update | Retrieval span (UTC) | Evidence-set SHA-256 |
| --- | ---: | --- | --- | --- |
| 2025-07 | 31 | 2026-06-04T16:19:07.000+02:00 | 2026-10-12T17:42:36.682896+00:00–2026-10-12T17:45:40.132811+00:00 | `487a81e3c8ff289bdaef6077fcf80fba159910d1f615cf6fcbfd8a323faba8d8` |
| 2025-08 | 31 | 2026-05-12T00:36:02.000+02:00 | 2026-10-12T17:45:45.986973+00:00–2026-10-12T17:48:39.969473+00:00 | `ad0a2d176baab940e9ae9a49a6a9d7e771a12ce2158deafdae971a2302f7304b` |
| 2025-09 | 30 | 2026-05-12T00:33:45.000+02:00 | 2026-10-12T17:48:46.624688+00:00–2026-10-12T17:51:32.168483+00:00 | `2dcb6dbbda935f4e3dbc2635ae8adb1fc83faa7b0116ca43d8c481e1dbd05f37` |

The complete Q3 evidence-set SHA-256 is
`68c43394661272e0e001b0c9d75a07951e27b8ce5d3c8905061b47e0fb128a90`.
The combined 228-manifest evidence-set SHA-256 is
`e49c9b3e3acd8fb1dd238528ad7dbf4c81d8df51e2206d00c3958d7dedd7abfc`.
Each digest uses successful records ordered by window start, window end and
retrieval ID, with lines of `<retrieval_id> <payload_sha256>\n`.

## Reproduce

First reconstruct the history through Q2 2025 as documented in the
[Q2 extension report](history-2025-q2-extension.md). Then request Q3 explicitly
as daily windows:

```bash
python -m electricity_pipeline --start 2025-07-01 --end 2025-09-30 --request-window day --database data/history.duckdb --raw-dir data/q3-2025-raw --export-dir data/history-exports
```

A later API retrieval may contain revisions. Exact offline reproduction instead
replays the 92 original daily manifests and their SHA-256-named payloads into the
Q2 reconstruction. Raw downloads, manifests and databases are excluded from Git.

## Limits and next step

This extension does not make 2025 complete and does not produce the final
two-year comparison. The next useful increment is October–December 2025,
followed by execution and verification of the guarded 2024–2025 history report.

Generation is not demand, prices or emissions; no such measures are inferred.
Renewable status follows the provider and source observations may be revised.

Independent educational analysis. Source data remain subject to
[Red Eléctrica's terms](https://www.ree.es/es/aviso-legal), not the code's MIT
license. See the [source contract](../docs/source-contract.md).
