# H1 2024: validated historical extension

Source: **Red Eléctrica de España, REData**. Geography: **peninsular Spain**.

## Coverage and verification

Executed on **2026-10-07**. This increment extends the verified warehouse from Q1 to **2024-01-01–2024-06-30**: **182 days**, **six complete months** and **2,004 actual technology observations**. Q2 adds **91 days and 1,002 observations**. Q1 observations and source lineage were verified against the original archived retrievals.

All **9 SQL quality checks** passed. Every calendar date is present, and technology observations remain separate from the 182 published system totals. The full **104-test offline suite**, Ruff lint and formatting checks also passed.

All **65 active retrieval manifests** were replayed into a separate empty warehouse with checksum verification. Generation rows, published totals and acquisition metadata matched exactly; all three analytical CSV exports matched byte for byte. The two-year history command still rejects this incomplete 2024–2025 dataset.

Maximum absolute daily reconciliation difference: **0.000000 MWh**. No missing measurements were imputed and no published totals were added to technology sums.

## Quarterly comparison

Both quarters contain **91 days**. Shares use total renewable MWh divided by total generation MWh; they are not averages of daily or monthly percentages. This is a quarter-on-quarter comparison within 2024, not a year-on-year result.

| Period | Days | Generation (GWh) | GWh/day | Renewable share |
| --- | ---: | ---: | ---: | ---: |
| 2024-Q1 | 91 | 63,725.797 | 700.283 | 61.49% |
| 2024-Q2 | 91 | 59,453.905 | 653.340 | 65.26% |
| H1 2024 | 182 | 123,179.702 | 676.812 | 63.31% |

Q2 generation changed by **-6.70%** from Q1; renewable share changed by **+3.78 percentage points**. Equal quarter lengths make the generation-total and daily-average relative changes identical. These observations do not identify weather, capacity or other causal drivers.

## Complete monthly periods

| Month | Days | Generation (GWh) | Renewable share |
| --- | ---: | ---: | ---: |
| 2024-01 | 31 | 22,019.078 | 54.30% |
| 2024-02 | 29 | 20,758.287 | 62.31% |
| 2024-03 | 31 | 20,948.432 | 68.22% |
| 2024-04 | 30 | 19,656.570 | 68.22% |
| 2024-05 | 31 | 19,758.288 | 66.19% |
| 2024-06 | 30 | 20,039.047 | 61.45% |

## Q2 technology observations

Provider names and renewable classifications are retained. Days observed count actual rows, not assumed zero generation on absent dates. In particular, `Fuel + Gas` is reported on only one Q2 day. This table must not be interpreted as a fully observed calendar for each technology.

| Source ID | Technology | Renewable | Days observed | Generation (GWh) |
| --- | --- | :---: | ---: | ---: |
| 1458 | Solar fotovoltaica | Yes | 91 | 13,672.145984 |
| 10291 | Eólica | Yes | 91 | 13,050.318569 |
| 1446 | Nuclear | No | 91 | 11,434.701869 |
| 10288 | Hidráulica | Yes | 91 | 9,468.014463 |
| 1454 | Ciclo combinado | No | 91 | 4,700.189970 |
| 10293 | Cogeneración | No | 91 | 3,673.346705 |
| 1459 | Solar térmica | Yes | 91 | 1,537.579148 |
| 10292 | Otras renovables | Yes | 91 | 944.882624 |
| 10289 | Carbón | No | 91 | 624.801249 |
| 10294 | Residuos no renovables | No | 91 | 219.486046 |
| 10295 | Residuos renovables | Yes | 91 | 128.438092 |
| 10290 | Fuel + Gas | No | 1 | 0.000001 |

## June sparse-series recovery

The April and May monthly requests passed directly. The June monthly response reported `Fuel + Gas` (ID `10290`) only on **2024-06-23**, at **0.001 MWh**, and failed the existing completeness contract. It was archived but never loaded.

June was then explicitly requested one day at a time. All **331 reported technology observations** (including names, classifications, energy and stored source percentages) and all **30 published totals** match the original monthly payload exactly. The one `Fuel + Gas` measurement is preserved; no rows were invented for its absent days.

Rejected monthly request: [2024-06-01–2024-06-30](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-01T00%3A00&end_date=2024-06-30T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741). Provider last update: 2026-01-13T17:55:06.000+01:00. Retrieved at: 2026-10-07T17:28:41.124622+00:00. SHA-256: `d063e50f9e241751c89b22ab8daa25c502d147df00115f68faa647fe66f65a90`.

## Reproduce

Use a new database to isolate H1 from any later loaded dates. Each daily/monthly response is independently validated and committed. A later API retrieval may contain revisions.

```bash
python -m electricity_pipeline --start 2024-01-01 --end 2024-02-29 --database data/h1-2024.duckdb --raw-dir data/h1-raw --export-dir data/h1-exports
python -m electricity_pipeline --start 2024-03-01 --end 2024-03-31 --request-window day --database data/h1-2024.duckdb --raw-dir data/h1-raw --export-dir data/h1-exports
python -m electricity_pipeline --start 2024-04-01 --end 2024-05-31 --database data/h1-2024.duckdb --raw-dir data/h1-raw --export-dir data/h1-exports
python -m electricity_pipeline --start 2024-06-01 --end 2024-06-30 --request-window day --database data/h1-2024.duckdb --raw-dir data/h1-raw --export-dir data/h1-exports
python -m electricity_pipeline.report --database data/h1-2024.duckdb
```

The baseline command prints monthly totals and the full retrieval evidence. The quarterly figures above come from this query against that database:

```sql
SELECT QUARTER(day) AS quarter, COUNT(*) AS days_observed,
       SUM(generation_mwh) / 1000 AS generation_gwh,
       SUM(generation_mwh) / 1000 / COUNT(*) AS generation_gwh_per_day,
       SUM(renewable_mwh) / SUM(generation_mwh) AS renewable_share
FROM daily_mix
WHERE region = 'peninsular' AND day BETWEEN '2024-01-01' AND '2024-06-30'
GROUP BY QUARTER(day)
ORDER BY quarter;
```

For exact offline reproduction, replay the original manifests with their SHA-256-named payloads into a separate database. Raw downloads, manifests and databases are excluded from Git; the evidence below identifies the snapshot.

## Source evidence

January–February acquisition timestamps and hashes are retained from the [initial coverage check](history-readiness-2024-2025.md). All 31 March acquisitions are retained from the [daily recovery](march-2024-daily-recovery.md). These Q1 observations and their source lineage were verified by replaying the original checksum-validated archives; no new Q1 downloads were used.

The following 32 successful acquisitions add April–June. They record original source publication and acquisition times, not replay times.

- Window: 2024-04-01–2024-04-30
  - Retrieval: `8ee3fa6083274bb39b676d3c7b2f5612`
  - Provider last update: 2026-01-13T17:58:06.000+01:00
  - Retrieved at: 2026-10-07T17:28:01.979438+00:00
  - SHA-256: `d26aa031f6446463a1977b77a428bce45434a035986453bbcd6e9971ad8b9f5c`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-04-01T00%3A00&end_date=2024-04-30T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-05-01–2024-05-31
  - Retrieval: `7bce768cae734e0080789fc5ea531d1f`
  - Provider last update: 2026-01-13T17:56:43.000+01:00
  - Retrieved at: 2026-10-07T17:28:30.582294+00:00
  - SHA-256: `aea5e036aaf152b8c108b469d340d38e45ee343a7ef322331c11be6eceb80fe6`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-05-01T00%3A00&end_date=2024-05-31T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-01–2024-06-01
  - Retrieval: `c0447a08339b4ca0a5421d987e0dcfc4`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:29:22.683344+00:00
  - SHA-256: `992c405cee1726b1776579875b4f75546269de607fc60c4fa86a3b60715e5a8a`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-01T00%3A00&end_date=2024-06-01T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-02–2024-06-02
  - Retrieval: `e41ceb6f2912474eb94be6a7568a18fa`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:29:32.017283+00:00
  - SHA-256: `e5e56bfc76436ee3b6944163e9c3bd35718b705610ffb7e786ef6c4c562ff9d1`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-02T00%3A00&end_date=2024-06-02T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-03–2024-06-03
  - Retrieval: `6b23da8f93cb43aba6b2c1172304c923`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:29:40.146862+00:00
  - SHA-256: `f3f279336b0ebbdd95fbcedb7a5518a4d079d982d1bdbd19d64a33fb9944a9b4`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-03T00%3A00&end_date=2024-06-03T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-04–2024-06-04
  - Retrieval: `3cfdc1a4a8d0437699504723d5773a16`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:29:49.121238+00:00
  - SHA-256: `d1702a2e23e23d922543d1f0eab13d0c82de8b8e45455f79332e39fb26e55597`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-04T00%3A00&end_date=2024-06-04T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-05–2024-06-05
  - Retrieval: `94fd3d118cc8464f8215c9d38d1c2beb`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:29:57.989262+00:00
  - SHA-256: `cb1e1cfd92c831bd9e62490a5102541a1c8e477ad7a90e7c25618053013a0655`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-05T00%3A00&end_date=2024-06-05T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-06–2024-06-06
  - Retrieval: `b4116bdf1a024defa0fee08302c423c0`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:30:14.604230+00:00
  - SHA-256: `24985708e41a99b29a468dfa9b7157a6fd596c6ebb1b0a1fb13b2af585e31857`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-06T00%3A00&end_date=2024-06-06T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-07–2024-06-07
  - Retrieval: `b12caad0bda143dba83e53815f7b8d47`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:30:23.264926+00:00
  - SHA-256: `82a2e7fd37b2ef0a1bf6337b57a3eff9fa0b16023c5b707e2baba0df850ba33f`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-07T00%3A00&end_date=2024-06-07T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-08–2024-06-08
  - Retrieval: `bddc428b71d14fe7871b1a77f5b4df41`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:30:30.318779+00:00
  - SHA-256: `4d622499de2a47754f6cb45cd4290caf3bb6511f88ce2228d04447fec193ec31`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-08T00%3A00&end_date=2024-06-08T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-09–2024-06-09
  - Retrieval: `72586b24205a404995087eacfb5fcc32`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:30:37.618137+00:00
  - SHA-256: `5fc4fcb8b2c5098457d736177379b13fd4c1fa80eb13e29a70a809a9994d761d`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-09T00%3A00&end_date=2024-06-09T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-10–2024-06-10
  - Retrieval: `b03ebedb2dc0485ea5ca84b61fd32fe2`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:30:46.789906+00:00
  - SHA-256: `1ff414889b7716cef555fbc7f23ec33a11b383c586a9ac35372382bf995efe04`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-10T00%3A00&end_date=2024-06-10T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-11–2024-06-11
  - Retrieval: `fbd0f4c06caa42868cffb9b28b67ab30`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:30:55.775650+00:00
  - SHA-256: `5dbe54b4dd4ae24c2f5aa87b689dd1789a62df7038060a115ef6a08c033ae019`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-11T00%3A00&end_date=2024-06-11T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-12–2024-06-12
  - Retrieval: `e94f1d4be2fd43afa206fb39197d1a37`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:31:03.951074+00:00
  - SHA-256: `38ee31cb5991ea8e312376c82b7178bd2203b3dffb37f3c1f57c4b6783a32226`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-12T00%3A00&end_date=2024-06-12T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-13–2024-06-13
  - Retrieval: `ecb98792d09f4f7a9289a5552c0708b8`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:31:11.525572+00:00
  - SHA-256: `104c28025061335d00c4ddb9ea75a4ac3faa2dccb4737ff36380a4cc0fa6ab22`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-13T00%3A00&end_date=2024-06-13T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-14–2024-06-14
  - Retrieval: `54ab746d587547ba83228fb248f913d0`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:31:19.731874+00:00
  - SHA-256: `fc7d7b7f75bcf2c93332e0d249f01ad570c1535e1fb9bfbc835c3e50c2252c85`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-14T00%3A00&end_date=2024-06-14T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-15–2024-06-15
  - Retrieval: `32160451dc544cb384b1e29c212607ac`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:31:28.037990+00:00
  - SHA-256: `55c4f24f249facc949d1b73c176b6c4a35caa457dc36cf71075ff527fbe23187`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-15T00%3A00&end_date=2024-06-15T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-16–2024-06-16
  - Retrieval: `028c2c1b13b0442aba9d517299e30a11`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:31:36.350891+00:00
  - SHA-256: `e2348b0ddbdc7a50debde9937f50accdeb8df28f59022d2214abd355a2d480b2`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-16T00%3A00&end_date=2024-06-16T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-17–2024-06-17
  - Retrieval: `47f03ae2f0464f718ab76a7b894e4f8b`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:31:50.870902+00:00
  - SHA-256: `dcaed58e470a2c2404ec72cb9487ce573aa77e8af9e90a59c6d445a2260d7ad0`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-17T00%3A00&end_date=2024-06-17T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-18–2024-06-18
  - Retrieval: `b89c56037a154f378e7d9f3a195600c9`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:32:25.233204+00:00
  - SHA-256: `039c839d05b39dd5d59731a31fbed719a016195314cbbd35a5be168e0ef9c8cf`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-18T00%3A00&end_date=2024-06-18T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-19–2024-06-19
  - Retrieval: `d197177b149d41b7877cd6bdbaaad382`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:32:32.327115+00:00
  - SHA-256: `b1bd07db2cd6ac7173ddf1b74508ffca9e2c0cb121c53ffca573ea5fa20d1e7f`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-19T00%3A00&end_date=2024-06-19T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-20–2024-06-20
  - Retrieval: `2e042e9d63584ea2809d2b8067c3b813`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:32:41.309668+00:00
  - SHA-256: `3cbccc5df934191dda7998d1f2cf059f9086d2973e1ea9fcc1a46b86b63ab83f`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-20T00%3A00&end_date=2024-06-20T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-21–2024-06-21
  - Retrieval: `2c25243785a244859b7566a940ee29ed`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:32:59.874153+00:00
  - SHA-256: `0cdbd56caf4229c74d57b63552426bb5aedb8a905c55a454eca13e08734517bb`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-21T00%3A00&end_date=2024-06-21T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-22–2024-06-22
  - Retrieval: `22f50d0be4a44722a6130a35cb19e4a0`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:33:07.933528+00:00
  - SHA-256: `825023d60be1a43a4e6eb0ea3c9c8d10d978cd1b686dded9d1df308a1875dbe8`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-22T00%3A00&end_date=2024-06-22T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-23–2024-06-23
  - Retrieval: `8547955b34e34b78979c32ddf8c1bc71`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:33:15.118420+00:00
  - SHA-256: `3dd3461710d12639f6af4b1a413de0d143b94e1adf49255d377047681a640972`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-23T00%3A00&end_date=2024-06-23T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-24–2024-06-24
  - Retrieval: `14ec6300fef54f24abd6c495f4aed244`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:33:22.267866+00:00
  - SHA-256: `cf3f276438687d59d47cf88b340aab6b53770f43b15e9b875800f4abe7431b77`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-24T00%3A00&end_date=2024-06-24T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-25–2024-06-25
  - Retrieval: `7bf77af6b453434a870fd3b29175517d`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:33:37.742124+00:00
  - SHA-256: `7ff781b4ea58596c28009317c5dac189631665d9b1aed3885d5195f6e82f33ff`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-25T00%3A00&end_date=2024-06-25T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-26–2024-06-26
  - Retrieval: `433d95d9001e4818966d459ec46b3c05`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:33:45.499164+00:00
  - SHA-256: `3f9688e718beb8e9a1e781d4283da874a71dc4fd9ba2fb2e5c8c2f54a20a151f`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-26T00%3A00&end_date=2024-06-26T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-27–2024-06-27
  - Retrieval: `248e3327ff274cf28dab8ebebd71f277`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:33:53.582912+00:00
  - SHA-256: `2345c81b6235b6ad41aef63303fc47b25f72e97abcbfa7d2dc7935cb544a6a46`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-27T00%3A00&end_date=2024-06-27T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-28–2024-06-28
  - Retrieval: `879675a647d642ffa492c7f6ab964124`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:34:01.708422+00:00
  - SHA-256: `f55b7336edab0fd7da6c4613660043703dd1df5dae23adee72f1b07db9be6435`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-28T00%3A00&end_date=2024-06-28T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-29–2024-06-29
  - Retrieval: `5905f580b0f14712b19aaacf2c83ba17`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:34:10.730583+00:00
  - SHA-256: `1a691d22f8deb872683087749f8d413a94c31e4b58882a710b3a12f7504a1714`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-29T00%3A00&end_date=2024-06-29T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Window: 2024-06-30–2024-06-30
  - Retrieval: `4acbadac896e4684826044f3e7471b9a`
  - Provider last update: 2026-01-13T17:55:06.000+01:00
  - Retrieved at: 2026-10-07T17:34:20.995802+00:00
  - SHA-256: `463a0d1cb44f1a6a2e10f5226aa63c6a49d86623f94a3bd01b926879176ce109`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-06-30T00%3A00&end_date=2024-06-30T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)

## Limits and next step

The remaining **July 2024–December 2025** history has not been validated in this increment. Six months do not establish a recurring seasonal pattern, and this report does not complete the multi-year milestone. Generation is not demand, prices or emissions; no such measures are inferred. Renewable status follows the provider and source observations may be revised.

Independent educational analysis. Source data remain subject to [Red Eléctrica’s terms](https://www.ree.es/es/aviso-legal), not the code’s MIT license. See the [source contract](../docs/source-contract.md).
