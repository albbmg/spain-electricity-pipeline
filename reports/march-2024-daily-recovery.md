# March 2024: verified daily acquisition

Source: **Red Eléctrica de España, REData**. Geography: **peninsular Spain**.

## Result

The original monthly response failed the completeness contract because `Fuel + Gas` had only one observation. Explicit one-day requests now recover the month under the unchanged validation rules. This result addresses the March acquisition blocker; it does not complete the 2024–2025 analysis.

- **31 validated days**, **342 actual technology observations**, **31 published totals** and **9 passing SQL quality checks**.
- The stored keys, technology names, renewable classifications, MWh values and source percentages match every reported technology observation in the original monthly payload. All 31 published totals match exactly.
- `Fuel + Gas` (ID `10290`) retains its one reported observation on 2024-03-18: **0.001 MWh**. The other daily responses omit that series. No zero-valued rows were added and no reported measurements were discarded.
- The monthly system summary is complete; the technology summary explicitly shows `days_observed = 1` for `Fuel + Gas`. Absence is not reinterpreted as a measured zero.
- Replaying all 31 manifests into a separate warehouse reproduced generation rows, published totals and original retrieval metadata exactly. All three analytical CSV exports matched byte for byte.
- Combining this validated month with the previously loaded January–February windows produces a complete **Q1 2024: 91 days and 1,002 technology observations**. The remaining 21 months of the intended two-year history are still pending.

Observed March generation: **20,948.432 GWh**; energy-weighted renewable share: **68.22%**. Maximum absolute daily reconciliation difference: **0.000000 MWh**. These describe this snapshot, not demand, prices, emissions or causal drivers.

## Reproduce

```bash
python -m electricity_pipeline --start 2024-03-01 --end 2024-03-31 --request-window day --database data/march-daily.duckdb --raw-dir data/march-raw --export-dir data/march-exports
```

The command deliberately makes 31 requests rather than retrying a rejected monthly response. Each day is an independent validated transaction. A failure stops subsequent requests and does not refresh exports. Monthly requests remain the default; data aggregation remains daily in both modes.

For exact offline reproduction, retain the manifests listed below beside their original SHA-256-named payloads and run `--replay-manifest` for each against a separate database. A later API retrieval may contain revised observations. Raw downloads and databases are excluded from Git.

## Original monthly evidence

The rejected monthly response has SHA-256 `c8917f26e0120c0bb7de89c4ed3ef54ea56c41ed88f942addfe42f4df58ece3c` and was retrieved at 2026-10-06T19:23:03.848575+00:00. See the [initial coverage check](history-readiness-2024-2025.md) for its request and publication timestamp.

## Daily retrieval evidence

All times retain their source or acquisition timezone. The URLs, original acquisition times and hashes identify the actual responses used for this verification.

- Date: 2024-03-01
  - Retrieval: `acd7513895aa410198aef348c2f2e4a9`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:54:53.865924+00:00
  - SHA-256: `9fe9441c4f52283db30168007b53c7ecdab019d3ad1cea58fb962a87807f4dd5`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-01T00%3A00&end_date=2024-03-01T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-02
  - Retrieval: `fb258a8b9507481db9af7c022fef7e71`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:55:02.278954+00:00
  - SHA-256: `a427ad0adf07897e0fb4e5c33438e7caa20cb535f8c94daeac53e166f6e8f218`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-02T00%3A00&end_date=2024-03-02T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-03
  - Retrieval: `45fad67960744c78bca92bf20d0700e3`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:55:08.845742+00:00
  - SHA-256: `68f52c34d944f034f1d923e88fdb8578a308503ad1044dd0eee07afd87e6a96e`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-03T00%3A00&end_date=2024-03-03T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-04
  - Retrieval: `565f5926493341a0a462dffbd186e3fb`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:55:17.677186+00:00
  - SHA-256: `b9b6a73a0e252a694c264e7188508c2c8fa4644ec66ed55a234692da36951a5d`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-04T00%3A00&end_date=2024-03-04T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-05
  - Retrieval: `b477d5da16054574a553e1d4a68ca7c1`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:55:24.864726+00:00
  - SHA-256: `335951c403ac68cf68bc0355ceecb9b769708bc94461189276982f2718b07b15`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-05T00%3A00&end_date=2024-03-05T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-06
  - Retrieval: `e44154f7ec3a423bbfd364a2f2186b0d`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:55:32.189210+00:00
  - SHA-256: `9372543fb57054ce4cd2aa7bf16a2678d83082bf366a56a1d736851f7213eb47`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-06T00%3A00&end_date=2024-03-06T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-07
  - Retrieval: `f500c73c85104b82bda86a46bb7ea196`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:55:38.534937+00:00
  - SHA-256: `df0700f858d4dcca54aa054f2791d4bc27ad8de50caa2fcd28d7debe9aa98381`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-07T00%3A00&end_date=2024-03-07T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-08
  - Retrieval: `25a4ee49059a44edb2c714fb5218618e`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:55:45.544803+00:00
  - SHA-256: `043c984b029726099d9a54f34ff04f55582a6125566231837ee818fb84e50bde`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-08T00%3A00&end_date=2024-03-08T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-09
  - Retrieval: `3dfc7ff537134949833a77d51bb6d573`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:55:51.640709+00:00
  - SHA-256: `56bca25cf3b389d9d9f4cb76ce2d8f1a3029f43938ee0b59f345db0653f6b6db`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-09T00%3A00&end_date=2024-03-09T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-10
  - Retrieval: `f335097bd72147fd8e990744111f143c`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:56:03.612397+00:00
  - SHA-256: `b58cc2b061f872380c93e45f02643d3e4a52c6cfda64b58e43eabaca6baf574a`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-10T00%3A00&end_date=2024-03-10T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-11
  - Retrieval: `1d0d467401f44b15b1f0b40267e0d41a`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:56:11.748194+00:00
  - SHA-256: `b68d6e394442b966090deef5f13122b81ee9c6c00aa26ca244145cb3cfb25370`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-11T00%3A00&end_date=2024-03-11T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-12
  - Retrieval: `95c40a4577da4058a69bfaf85ac16aa2`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:56:29.439144+00:00
  - SHA-256: `4e6a2d4a2732868570bc066e6d95ae2b914f458f609e8abf2848e2072b8a9690`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-12T00%3A00&end_date=2024-03-12T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-13
  - Retrieval: `789279988a57426eb6a74e275086d2dc`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:56:35.575102+00:00
  - SHA-256: `5130006176c81211c7cecb7b41e18d8b0bd6c3ebe9e4d529563e55ea13bd2fe3`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-13T00%3A00&end_date=2024-03-13T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-14
  - Retrieval: `22b3a12214ec4e2bba89917d6ffb39b0`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:56:43.834737+00:00
  - SHA-256: `215a7c4c2af589acce524ebe1900dfbaa840cba9f851de8b4aaceba0d5a5ac45`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-14T00%3A00&end_date=2024-03-14T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-15
  - Retrieval: `850adcd6e61a4bc3abec080a7c6e06cd`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:56:52.674394+00:00
  - SHA-256: `6cb5aff1bbcc0de412868d92f5957d821c2f6813d189539f6af002f365d220c7`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-15T00%3A00&end_date=2024-03-15T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-16
  - Retrieval: `9ed0adb7c4e144b485c67034710ce577`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:57:00.442038+00:00
  - SHA-256: `825e2cd100df4fd673cd25bb385a7963c440b72acbbbaeb8b44b0e14584fbef1`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-16T00%3A00&end_date=2024-03-16T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-17
  - Retrieval: `8d57ded46d6f4694a8aa1573c20c66ec`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:57:06.630197+00:00
  - SHA-256: `0b0499bfe937ca55bdd8ba4656c8f3c2d61f55b4617d6a506a11447262a69520`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-17T00%3A00&end_date=2024-03-17T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-18
  - Retrieval: `8cd19df7724048d0ad173c9d09825ae4`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:57:18.231826+00:00
  - SHA-256: `c9b3eea167d2242c8c1930cc9c1f4aa8009c64d4ae949be114aada516a69899c`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-18T00%3A00&end_date=2024-03-18T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-19
  - Retrieval: `b19c92f8be614163906690fd98950230`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:57:25.240077+00:00
  - SHA-256: `4ce9afdc45ba9f602a0f277a70ebce3849bf4e5cc97d2812d4e6fa08123b8218`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-19T00%3A00&end_date=2024-03-19T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-20
  - Retrieval: `a5c80322677c4e8ba65178aed4ba0686`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:57:33.322285+00:00
  - SHA-256: `f9571e15030d159eeb8bfe1a479d64778e4f3002230376191b67e23d8d29e90b`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-20T00%3A00&end_date=2024-03-20T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-21
  - Retrieval: `9608f43205554d1f950a92c32e0a9c32`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:57:40.883730+00:00
  - SHA-256: `3916d0a71c42c4e53a4ac095f9acbdb371084ffc4cccd3824bad51f63b6c2691`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-21T00%3A00&end_date=2024-03-21T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-22
  - Retrieval: `d4b06a3015764c7fbf91e0e3844be49c`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:57:47.702184+00:00
  - SHA-256: `c173f42f968bc7bc5aecbd704386a565da1182a2511ee3e781e31402bd0a4d2d`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-22T00%3A00&end_date=2024-03-22T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-23
  - Retrieval: `bd61d3d52fa8422cb513c90a5ca5294c`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:58:05.159911+00:00
  - SHA-256: `ca78244425aedecaba1d4b3d6a9ad547499d63f2e7d7e3f640d5a4770db59fd7`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-23T00%3A00&end_date=2024-03-23T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-24
  - Retrieval: `0ec02c65faea42edb2e5d1195011262e`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:58:12.109397+00:00
  - SHA-256: `2f13a91457e55bd45f0d8639ae3f0fbb3777b79fe360046c1b66622d9f643a3f`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-24T00%3A00&end_date=2024-03-24T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-25
  - Retrieval: `136a3b411a1443ac9bcf343d21600163`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:58:19.020786+00:00
  - SHA-256: `4412113edacff9af7a7e38dc43c81fd3ed4acd53f34d27af606ba228da8a0f6d`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-25T00%3A00&end_date=2024-03-25T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-26
  - Retrieval: `2df8071b28a84261aaf6d653cfcab9b6`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:58:25.994897+00:00
  - SHA-256: `b01040258e443a49ae43d5aab835ffb6987e74ab867557c88ed91b12fd18983d`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-26T00%3A00&end_date=2024-03-26T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-27
  - Retrieval: `def57ae8078a4dbda5fc01c929fbc034`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:58:32.616588+00:00
  - SHA-256: `a9eb75c3aac6fd02596cbfba788a97efe18b4ae30ba6456ebff0992a3f6565fa`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-27T00%3A00&end_date=2024-03-27T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-28
  - Retrieval: `ee3cda9491f64cf5bbab80eba6d956d3`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:58:41.375947+00:00
  - SHA-256: `b7289d3166ced7865440aa12ecbcad2ba77b77301493c9617582bdde7f8fea83`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-28T00%3A00&end_date=2024-03-28T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-29
  - Retrieval: `be0ce097b92f4f0282a498c0c54bfff1`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:58:49.538426+00:00
  - SHA-256: `4eaf4e36252765943cc529de2026baa21c848a81d0114ec7c0fd09d3fc34f47c`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-29T00%3A00&end_date=2024-03-29T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-30
  - Retrieval: `6854a13d1c2f423ba2e6148a5ef3bb56`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:58:56.454164+00:00
  - SHA-256: `6ffb7b97e9847cd27928335e31a8caf2b5a358b5705cd9d834dffa7e9c6d842a`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-30T00%3A00&end_date=2024-03-30T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)
- Date: 2024-03-31
  - Retrieval: `093810e38f3e400d98ca35b8d133b0f0`
  - Provider last update: 2026-01-13T18:00:33.000+01:00
  - Retrieved at: 2026-10-06T19:59:03.303804+00:00
  - SHA-256: `183e6d7472de0f389ac6ed3bc36ac49d15ad18cd179c888dcab2527c55fd36fb`
  - [Source request](https://apidatos.ree.es/es/datos/generacion/estructura-generacion?start_date=2024-03-31T00%3A00&end_date=2024-03-31T23%3A59&time_trunc=day&geo_trunc=electric_system&geo_limit=peninsular&geo_ids=8741)

Independent educational analysis. Source data remain subject to [Red Eléctrica’s terms](https://www.ree.es/es/aviso-legal), not the code’s MIT license. See the [source contract](../docs/source-contract.md).
