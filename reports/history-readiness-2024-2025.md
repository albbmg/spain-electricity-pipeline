# Historical coverage check: 2024–2025

Source: **Red Eléctrica de España, REData**. Geography: **peninsular Spain**.

Checked on 2026-10-06 using the production ingestion and validation path in a separate warehouse. The intended 2024–2025 baseline is **not complete**; no annual or seasonal findings are published from this partial load.

**Follow-up on 2026-10-06:** explicit daily requests recovered March without imputation,
and every reported observation and total matches the original monthly payload.
See the [verified recovery](march-2024-daily-recovery.md). The initial monthly failure
below is retained as diagnostic evidence; the full two-year analysis remains pending.

## Observed result

- January and February 2024 passed validation: 60 days, 660 technology observations and 60 published totals.
- The March 2024 response contains 31 observations for each other returned technology and the published total, but only one for `Fuel + Gas` (source ID `10290`): 2024-03-18, 0.001 MWh.
- The other 30 daily values for that technology are absent. The response does not explicitly label them as zero.
- The existing completeness contract rejected March before loading it. The first two committed windows remain intact. Subsequent months were not requested in this run.
- The historical report command correctly rejected the partial warehouse rather than producing annual comparisons.

## Investigation proposed after the initial failure

Investigate the provider’s sparse-series semantics or retrieve the affected dates at a narrower request grain and validate the returned observations. Do not fill missing measurements with zero, drop the technology, or weaken reconciliation solely to obtain a report. Complete and validate all requested calendar dates before marking historical analysis finished.

## Retrieval evidence

- Window: 2024-01-01–2024-01-31
  - Retrieval: `c0f20c8a0eec48e7bf053247393472c1`
  - Provider last update: 2025-01-28T16:56:22.000+01:00
  - Retrieved at: 2026-10-06T19:22:39.592019+00:00
  - SHA-256: `b00295ffcf9c28d8cced00fb36e67ea1e4871acdaa8f9d895c0aaf3166c75e4e`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-01-01T00%3A00&end_date=2024-01-31T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-02-01–2024-02-29
  - Retrieval: `453e5d668e7949fe815f63a81387cb60`
  - Provider last update: 2026-01-13T18:01:50.000+01:00
  - Retrieved at: 2026-10-06T19:22:49.696215+00:00
  - SHA-256: `409ea2ebe0c17b4c583cb8c0712234c35fa550633ad8ecaa9327968317580485`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-02-01T00%3A00&end_date=2024-02-29T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-03-01–2024-03-31
  - Retrieval: `06eefdc12e9841a6b768ab3953f2b846`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:23:03.848575+00:00
  - SHA-256: `c8917f26e0120c0bb7de89c4ed3ef54ea56c41ed88f942addfe42f4df58ece3c`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-01T00%3A00&end_date=2024-03-31T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)

Raw payloads and manifests remain outside Git. The rejected payload is retained locally as diagnostic evidence; its retrieval is not a successful warehouse load.

## Reproduce the check

```bash
python -m electricity_pipeline --start 2024-01-01 --end 2025-12-31 --database data/history.duckdb --raw-dir data/history-raw --export-dir data/history-exports
python -m electricity_pipeline.history --database data/history.duckdb --start-year 2024 --end-year 2025
```

The first command currently exits unsuccessfully at the documented March response; the second refuses the incomplete history. Source revisions may change this outcome. The report generator itself is covered by offline tests with explicitly synthetic complete years, including leap days, energy-weighted shares and missing-period rejection.

Independent educational analysis. Source data remain subject to [Red Eléctrica’s terms](https://www.ree.es/es/aviso-legal), not the code’s MIT license. See the [source contract](../docs/source-contract.md).
