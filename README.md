# Spain Electricity Pipeline

A reproducible data pipeline for understanding the **generation mix of the Spanish
peninsular electricity system**, using the public Red Eléctrica REData API.

The first milestone focuses on trustworthy ingestion: retrieving historical daily
generation, preserving source evidence, reconciling technologies with the published
total and loading repeatable date partitions. SQL reporting and CSV exports follow
the ingestion contract.

## Questions

- How does renewable generation's share change across days and months?
- Which technologies account for the changes in the generation mix?
- Can the reported totals be reconciled with their underlying observations?
- How can a revised API response replace an earlier load without duplicating data?

## Approach

**REData REST API → immutable raw JSON → validation → DuckDB → SQL marts → CSV**

Python handles acquisition and contracts. DuckDB keeps the analytical model runnable
locally without a server or cloud account. Versioned SQL owns the metric definitions.

Scope is deliberately explicit: **peninsular Spain**, daily generation, historical
closed dates. Generation is not electricity demand, prices, customer bills or carbon
emissions. The project does not infer those measures from the generation mix.

See [the source contract](docs/source-contract.md) and [the roadmap](docs/roadmap.md).

## Source and attribution

Source: **Red Eléctrica de España, REData**.

- [API documentation](https://www.ree.es/en/datos/apidata)
- [Generation methodology and glossary](https://www.ree.es/es/datos/generacion/estructura-generacion)
- [Source terms](https://www.ree.es/es/aviso-legal)

This is an independent educational analysis. REData data remain subject to the
provider's terms; they are not relicensed by this repository. Raw downloads and the
local database are excluded from Git. Published analytical results must retain
source attribution and the source-update and retrieval dates. There is no affiliation
with Red Eléctrica.

Project code is available under the [MIT License](LICENSE).
