# Validated baseline

Source: **Red Eléctrica de España, REData**. Geography: **peninsular Spain**.

Period: **2025-01-01–2025-03-31**. **90 observed days**, **990 technology observations**, **11 technologies**.

Generation: **66,409.067 GWh**. Energy-weighted renewable share: **59.05%**.

| Month | Days | Complete month | Generation (GWh) | Renewable share |
| --- | ---: | :---: | ---: | ---: |
| 2025-01 | 31 | Yes | 23,203.957 | 57.59% |
| 2025-02 | 28 | Yes | 20,550.294 | 55.82% |
| 2025-03 | 31 | Yes | 22,654.816 | 63.47% |

All **9 SQL quality checks** passed.

## Source evidence

Only retrievals currently referenced by analytical observations are listed.

- Window: 2025-01-01–2025-01-31
  - Provider last update: 2026-05-11T19:41:15+00:00
  - Retrieved at: 2026-10-05T18:02:35.034984+00:00
  - SHA-256: `43cc55a1353eb357ba44882ebf46bca4338affa102b10cd6b9f00e393a1b44e4`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2025-01-01T00%3A00&end_date=2025-01-31T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2025-02-01–2025-02-28
  - Provider last update: 2026-05-11T19:39:59+00:00
  - Retrieved at: 2026-10-05T18:02:51.911064+00:00
  - SHA-256: `8e00149b9a4d4dd527b6d31d2e6ca3ace7f977646dbd144bf4331eeabc9309cd`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2025-02-01T00%3A00&end_date=2025-02-28T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2025-03-01–2025-03-31
  - Provider last update: 2026-05-11T21:47:38+00:00
  - Retrieved at: 2026-10-05T18:03:04.975164+00:00
  - SHA-256: `e005270eb4deca8e067ead84f3388036f8abe6bd89c18db15d8140d3fec2360d`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2025-03-01T00%3A00&end_date=2025-03-31T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)

## Interpretation limits

These are historical generation observations, not demand, prices or emissions. Renewable status follows the provider's classification. The API's total is excluded from technology sums and used only for reconciliation. Source data may be revised; a later retrieval can legitimately change this baseline. No causal or year-on-year conclusions follow from this initial snapshot.

Reproduce with `python -m electricity_pipeline.report`. See [the source contract](../docs/source-contract.md) and [provider terms](https://www.ree.es/es/aviso-legal).
