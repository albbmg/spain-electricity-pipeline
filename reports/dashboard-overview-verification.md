# Offline dashboard overview verification

Executed on 2026-10-15 against the validated 2024–2025 warehouse and its separately
replayed counterpart. Source: **Red Eléctrica de España, REData**; geography:
**peninsular Spain**. This is a static snapshot, not a live refresh.

| Selection | Days | Months | Generation (GWh) | Renewable share | Active retrievals |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2024 | 366 | 12 | 248,642.883 | 58.96% | 130 |
| 2025 | 365 | 12 | 258,120.232 | 57.54% | 101 |
| 2024–2025 | 731 | 24 | 506,763.115 | 58.24% | 231 |

Generation and renewable share match the [historical report](history-2024-2025.md).
Shares use summed renewable energy divided by summed generation. The source's
published total remains a separate reconciliation control.

## Executed checks

- `ruff check .` and `ruff format --check .` passed.
- All 111 offline pytest tests passed, including seven dashboard cases.
- Generating the HTML from the original and replay warehouses produced identical
  bytes. The original warehouse's SHA-256 was unchanged after generation.
- The built Python wheel included the dashboard module and its HTML template.
- Chromium with Playwright, with its browser context offline, loaded the local
  HTML and exercised the 2024, 2025 and combined-period filters. KPI strings,
  monthly row counts, leap-day coverage and filtered retrieval counts matched.
- Keyboard selection updated the indicators. A 390-pixel viewport had no page
  overflow. Desktop (1280 pixels) and mobile captures were visually inspected.
- No JavaScript exceptions or HTTP requests occurred during these interactions.

## Reproduction and limits

```bash
python -m electricity_pipeline.dashboard --database data/history.duckdb --start-year 2024 --end-year 2025 --output data/dashboard.html
```

Open the HTML locally, change the period, and expand monthly values and source
evidence. The output directory must exist. To reproduce the exact data snapshot,
use the original trusted manifests and payloads described in the
[historical completion evidence](history-2025-q4-completion.md). Raw evidence and
databases are not committed. Original acquisition dates, provider update dates and
checksums remain visible in the generated report and historical source evidence;
this verification date does not replace any of them.

This overview does not yet include technology-level filters or YoY visuals.
Testing in Chromium does not establish compatibility with every browser or replace
a full accessibility audit. Power BI is optional and has not been implemented.

Source data remain subject to [Red Eléctrica's terms](https://www.ree.es/es/aviso-legal),
not the project's MIT code license. Keep attribution and source dates when sharing.
