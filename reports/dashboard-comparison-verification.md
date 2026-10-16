# Offline dashboard comparable-period verification

Executed on 2026-10-16 using explicitly **synthetic** complete calendar years.
This verifies the implementation, not a refresh of the real REData snapshot.
The original 2024–2025 warehouse and archives were not available for this run;
the earlier [real-data report](history-2024-2025.md) remains separate evidence.

## Behavior and numeric checks

The new panel compares the selected current month with the same month one year
earlier in the exported history. Its table contains both calendar-day counts,
generation, daily-average generation, energy-weighted renewable shares, YoY
percentages and share changes in percentage points. The first year has an explicit
unavailable state. The prior year can fall outside the current UI year selection,
but older warehouse years cannot leak into the exported comparison range.

All displayed monthly comparisons matched the historical report generated from the
same synthetic warehouse. February 2024 has 29 days and February 2025 has 28:
doubling daily generation changes the monthly total by **+93.10%**, not +100%,
while daily-average growth is **+100.00%**. Separate tests cover decreases and an
unchanged daily average despite different month lengths. Shares of 8.6249% and
10.0051% produce **+1.38 pp** using exact inputs, not +1.39 pp from displayed shares.
These are test values, not observations about Spain.

Evidence is joined through the observations currently used by each month, including
multiple active retrievals after a partial replacement. Tests reject leakage of an
unreferenced retrieval record with the same window. Update timestamps, retrieval
timestamps and checksums remain grouped by the observation month they support.

## Executed validation

- `ruff check .` and `ruff format --check .` passed.
- All **119 pytest tests** passed in an isolated Python environment.
- Real Chromium **153.0.8010.0**, driven by Playwright with its context offline,
  verified **48 period/month comparison selections**, including unavailable states,
  every displayed metric and both months' exact source-evidence strings.
- All **144 technology-filter combinations** still passed. Technology selections
  did not change the comparison, overview indicators or period-level evidence.
- Keyboard month selection updated the comparison and evidence. Valid month
  selection persisted across a compatible period change; incompatible changes reset
  to the latest month. Switching to the first year hid and cleared prior results.
- Desktop (1280 px) and mobile (390 px) captures were visually inspected. Narrow
  screens scroll the comparison table independently; the page did not overflow.
  No JavaScript exceptions or HTTP requests occurred.

## Reproduction and limits

With project development dependencies, Node.js Playwright and Chromium installed:

```bash
mkdir -p data
pytest tests/test_dashboard.py --basetemp data/comparison-check -q
node tests/browser/dashboard.cjs data/comparison-check/test_technology_html_for_brows0/synthetic-dashboard.html
```

The script optionally accepts a Chromium executable and screenshot directory as
its second and third arguments. `--basetemp` replaces the specified test directory;
do not use a source archive or an existing warehouse directory. Synthetic HTML is
explicitly labeled and is not committed. Browser checks remain a local supplement
to the Python CI suite, not a complete accessibility or cross-browser audit.

Source attribution for real outputs remains **Red Eléctrica de España, REData**;
scope is **peninsular Spain**. Published totals remain separate controls, never
additional generation. The daily average adjusts calendar length, not weather or
other causes. Preserve source dates, checksums and
[provider terms](https://www.ree.es/es/aviso-legal), separate from the MIT code license.
The portable portfolio example and its final delivery are still pending.
