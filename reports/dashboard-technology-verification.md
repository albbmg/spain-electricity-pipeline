# Offline dashboard technology verification

Executed on 2026-10-15 using **explicitly synthetic** 2024–2025 calendar years,
with an additional 2023 year to detect selection leakage. This verifies software
behavior, not new findings about Spain's electricity generation. The earlier
real-data overview verification remains documented separately; its local warehouse
and archived payloads were unavailable for this run, so no new real-data replay or
technology measurements are claimed here.

## Implemented behavior

The month and classification selectors filter a technology table with source IDs,
renewable flags, GWh, observed/calendar-day counts and shares of full-month system
generation. The overview and source evidence retain the Period selector's scope.
Source totals remain separate. All numeric display values are calculated with
Python Decimal; the browser only selects already calculated rows.

Absent series produce no rows, while recorded zeros remain visible. Name and
classification variants under the same source ID remain separate; different IDs
with the same label are not merged. A month with no observations in the selected
classification has an explicit empty state. Shares are never renormalized after
filtering. The interface explains partial coverage and rounding.

## Executed checks

- `ruff check .` and `ruff format --check .` passed.
- All 114 offline pytest tests passed, including ten dashboard cases.
- Independent SQL over `generation` matched every displayed technology attribute,
  energy, day count and share across the 24 selected months. Exact monthly technology
  sums matched the system totals. The extra 2023 year was excluded.
- Synthetic February 2024 exercised 29 calendar days, a one-day 100 MWh series,
  one measured-zero day, duplicate labels under distinct IDs, and changes of name
  and renewable classification. February 2025 used 28 days. An absent series in
  March 2025 remained absent rather than being filled with zeros.
- Chromium 153.0.8010.0 with Playwright loaded the local HTML with the browser
  context offline and verified all **144 period/month/classification combinations**.
  Table cells matched the Python snapshot already checked against source SQL.
  Filtering left overview indicators and selected-period evidence unchanged.
- Keyboard selection updated the table; Tab reached its focusable horizontal-scroll
  region. Month selection survived a compatible period change and reset to the
  latest month when necessary. Empty-state visibility and measured-zero rows passed.
- Desktop (1280 px) and mobile (390 px) captures were visually inspected. The page
  had no horizontal overflow; the wide table was independently scrollable on mobile.
  No JavaScript exceptions or HTTP requests occurred.

## Reproduce the synthetic browser checks

Install the project's development dependencies and a Node.js Playwright installation
with Chromium. Python tests do not require Node or a browser; this is an additional
local check. In a clean checkout, with `playwright` available to Node:

```bash
mkdir -p data
pytest tests/test_dashboard.py --basetemp data/dashboard-check -q
node tests/browser/dashboard.cjs data/dashboard-check/test_technology_html_for_brows0/synthetic-dashboard.html
```

The test's temporary HTML is explicitly headed **Synthetic verification data**.
`--basetemp` replaces that test directory; do not point it at stored source evidence.
Optional second and third script arguments specify a Chromium executable and a
directory for screenshots. No synthetic databases, raw payloads or generated HTML
are committed. Browser checks are not yet part of GitHub Actions, which runs the
Python suite. Chromium testing is not a full accessibility or cross-browser audit.

Real-data outputs must retain **Red Eléctrica de España, REData** attribution,
peninsular geography, retrieval/update dates and checksums. Provider data remain
subject to [Red Eléctrica's terms](https://www.ree.es/es/aviso-legal), separate from
the project's MIT code license. This change does not refresh the historical snapshot.
