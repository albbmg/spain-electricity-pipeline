# Q1 2025: verified offline integration into history

Source: **Red Eléctrica de España, REData**. Geography: **peninsular Spain**.

## Scope

Executed on **2026-10-10** without an API request. The three original Q1 2025
manifests were checksum-verified and replayed into a freshly reconstructed 2024
historical warehouse.

The resulting coverage is **2024-01-01–2025-03-31**: **456 consecutive days**,
**15 complete months**, **5,020 actual technology observations** and **456
published system totals**. Source totals remain separate from technology rows.

## Integration verification

- All **4,030 technology observations** and **366 published totals** from 2024
  remained exactly unchanged after the three Q1 replays.
- Q1 2025 added **990 technology observations** and **90 published totals**.
  The revision audit recorded only additions: no changed, removed or unchanged
  rows in those previously empty dates.
- A separate Q1-only replay matched the original baseline warehouse exactly for
  generation rows, published totals and acquisition metadata. Its three CSV
  exports matched the original baseline exports byte for byte.
- All **133 active manifests** were replayed into another empty warehouse.
  Generation rows, published totals, acquisition metadata and all three
  combined-history CSV exports matched exactly.
- All **9 SQL quality checks** passed, with no missing calendar dates or
  duplicate source keys.
- The two-year history command still rejects the selection because
  April–December 2025 are absent.

The integrated Q1 snapshot contains **66,409.067 GWh** of generation and an
energy-weighted renewable share of **59.05%**, matching the
[original Q1 baseline](baseline-2025-q1.md).

## Source evidence

These are the original acquisition timestamps and provider publication times,
not replay times:

| Window | Retrieval ID | Provider update | Retrieved at (UTC) | SHA-256 |
| --- | --- | --- | --- | --- |
| [2025-01-01–2025-01-31](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2025-01-01T00%3A00&end_date=2025-01-31T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741) | `e4070fca3561423f99950b8790148713` | 2026-05-11T21:41:15.000+02:00 | 2026-10-05T18:02:35.034984+00:00 | `43cc55a1353eb357ba44882ebf46bca4338affa102b10cd6b9f00e393a1b44e4` |
| [2025-02-01–2025-02-28](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2025-02-01T00%3A00&end_date=2025-02-28T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741) | `1ff4f5c550674f66872d0ab2d7efbf11` | 2026-05-11T21:39:59.000+02:00 | 2026-10-05T18:02:51.911064+00:00 | `8e00149b9a4d4dd527b6d31d2e6ca3ace7f977646dbd144bf4331eeabc9309cd` |
| [2025-03-01–2025-03-31](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2025-03-01T00%3A00&end_date=2025-03-31T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741) | `077ecfc5b01a452ba51b8181b29e1901` | 2026-05-11T23:47:38.000+02:00 | 2026-10-05T18:03:04.975164+00:00 | `e005270eb4deca8e067ead84f3388036f8abe6bd89c18db15d8140d3fec2360d` |

The Q1 evidence-set SHA-256 is
`513d4ee00a6450981a16c6061c55defe9b8be2817d25d70ef429fb4f3b8ff260`.
The combined 133-manifest evidence-set SHA-256 is
`74597029ae191a5b611e1e1f58469c111acfa7bb4352e72e8c9d636e10c29a27`.
Each digest uses records ordered by window start, window end and retrieval ID,
with lines of `<retrieval_id> <payload_sha256>\n`.

## Reproduce the integration

First reconstruct 2024 as documented in the
[full-year report](baseline-2024-full-year.md). Then replay the trusted Q1
archives into that database:

```bash
python -m electricity_pipeline --replay-manifest data/raw/e4070fca3561423f99950b8790148713.manifest.json --database data/history.duckdb --export-dir data/history-exports
python -m electricity_pipeline --replay-manifest data/raw/1ff4f5c550674f66872d0ab2d7efbf11.manifest.json --database data/history.duckdb --export-dir data/history-exports
python -m electricity_pipeline --replay-manifest data/raw/077ecfc5b01a452ba51b8181b29e1901.manifest.json --database data/history.duckdb --export-dir data/history-exports
```

The manifests and their SHA-256-named payloads must remain together. Raw
downloads, manifests and databases are excluded from Git.

## Limits and next step

This integration does not make 2025 complete and does not produce a two-year
comparison. The next useful increment is April–June 2025, followed by
July–December 2025 and execution of the guarded 2024–2025 history report.

Generation is not demand, prices or emissions; no such measures are inferred.
Renewable status follows the provider and source observations may be revised.

Independent educational analysis. Source data remain subject to
[Red Eléctrica's terms](https://www.ree.es/es/aviso-legal), not the code's MIT
license. See the [source contract](../docs/source-contract.md).
