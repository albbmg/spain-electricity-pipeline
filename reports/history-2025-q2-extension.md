# Q2 2025: verified history extension

Source: **Red Eléctrica de España, REData**. Geography: **peninsular Spain**.

## Scope

Executed on **2026-10-11**. Three monthly API responses for April–June 2025
passed the existing source contract directly, were archived with their checksums
and were loaded into a fresh reconstruction of the previously verified history.

The resulting coverage is **2024-01-01–2025-06-30**: **547 consecutive days**,
**18 complete months**, **6,021 actual technology observations** and **547
published system totals**. Source totals remain separate from technology rows.

## Integration verification

- The pre-existing **5,020 technology observations**, **456 published totals**
  and **133 acquisition records** through 2025-03-31 remained exactly unchanged.
- Q2 2025 added **1,001 technology observations** and **91 published totals**.
  The revision audit recorded only additions: no changed, removed or unchanged
  rows in those previously empty dates.
- All **136 active manifests** were checksum-verified and replayed into another
  empty warehouse. Generation rows, published totals and acquisition metadata
  matched the live-integrated warehouse exactly.
- All three replayed CSV exports matched the live-integrated exports byte for
  byte. All **9 SQL quality checks** passed, with no missing calendar dates or
  duplicate source keys.
- The two-year history command still rejects the selection because
  July–December 2025 are absent.

## Descriptive check

Q2 2025 contains **60,834.284 GWh** of generation and an energy-weighted
renewable share of **62.00%**. The same calendar quarter has 91 days in both
years, so total and per-day changes are equal after rounding.

| Period | Days | Generation (GWh) | GWh/day | Renewable generation (GWh) | Renewable share |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2024-Q2 | 91 | 59,453.905 | 653.340 | 38,801.379 | 65.26% |
| 2025-Q2 | 91 | 60,834.284 | 668.509 | 37,714.343 | 62.00% |
| Observed change | — | +2.32% | +2.32% | -2.80% | -3.27 pp |

This is a like-calendar-quarter descriptive check, not the guarded two-year
report and not evidence of a cause. Q2 2024 has 1,002 technology observations
and Q2 2025 has 1,001 because the source technology set can vary by day; no
missing technology values were inferred or filled.

## Source evidence

| Window | Retrieval ID | Provider update | Retrieved at (UTC) | SHA-256 |
| --- | --- | --- | --- | --- |
| [2025-04-01–2025-04-30](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2025-04-01T00%3A00&end_date=2025-04-30T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741) | `2c40c005923149f9934a1c9bd789511c` | 2026-05-11T23:46:22.000+02:00 | 2026-10-11T17:08:31.271312+00:00 | `13cb3f3d8577b9ce9ebfcf19f79305d7f3444baee83fd0b477eecf637fa7df1d` |
| [2025-05-01–2025-05-31](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2025-05-01T00%3A00&end_date=2025-05-31T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741) | `64397da5190343cfaaad5bb5ef5461b8` | 2026-05-11T23:45:06.000+02:00 | 2026-10-11T17:08:36.905653+00:00 | `0f56f8845245652cb78b51860a35e97645ddea1460d2ae48b53c2b4d17077c93` |
| [2025-06-01–2025-06-30](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2025-06-01T00%3A00&end_date=2025-06-30T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741) | `97a943f371d944969ae867b064eb7c2e` | 2026-05-11T23:42:49.000+02:00 | 2026-10-11T17:08:43.457141+00:00 | `f9287206c886bb287520b6fc0dabd20e17fb16a9ea779058a890dc5801f87c3f` |

The Q2 evidence-set SHA-256 is
`d8a344e2471098d8a40e42bb3262e343b982f08ae8081b38b05d16f38cb199e7`.
The combined 136-manifest evidence-set SHA-256 is
`fe20df358523dff2d3faea8464b33d989a0fde86fce1d3f997fe7f2857911f51`.
Each digest uses records ordered by window start, window end and retrieval ID,
with lines of `<retrieval_id> <payload_sha256>\n`.

## Reproduce the extension

First reconstruct the history through Q1 2025 as documented in the
[Q1 integration report](history-2025-q1-integration.md). Then replay the trusted
Q2 archives into that database:

```bash
python -m electricity_pipeline --replay-manifest data/q2-2025-raw/2c40c005923149f9934a1c9bd789511c.manifest.json --database data/history.duckdb --export-dir data/history-exports
python -m electricity_pipeline --replay-manifest data/q2-2025-raw/64397da5190343cfaaad5bb5ef5461b8.manifest.json --database data/history.duckdb --export-dir data/history-exports
python -m electricity_pipeline --replay-manifest data/q2-2025-raw/97a943f371d944969ae867b064eb7c2e.manifest.json --database data/history.duckdb --export-dir data/history-exports
```

The manifests and their SHA-256-named payloads must remain together. Raw
downloads, manifests and databases are excluded from Git.

## Limits and next step

This extension does not make 2025 complete and does not produce a two-year
comparison. The next useful increment is July–September 2025, followed by
October–December 2025 and execution of the guarded 2024–2025 history report.

Generation is not demand, prices or emissions; no such measures are inferred.
Renewable status follows the provider and source observations may be revised.

Independent educational analysis. Source data remain subject to
[Red Eléctrica's terms](https://www.ree.es/es/aviso-legal), not the code's MIT
license. See the [source contract](../docs/source-contract.md).
