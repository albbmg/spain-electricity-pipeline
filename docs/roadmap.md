# Small, verifiable milestones

Work one coherent change at a time. A milestone is complete only after execution
and verification; a plan or specification is not an implemented feature.

- [x] **Source contract** — define geography, grain, units, failure rules and questions.
- [x] **Acquisition and validation** — bounded requests, retry policy, raw evidence,
   completeness checks, total reconciliation and tests with explicitly synthetic data.
- [x] **Analytical storage** — transactional window replacement, SQL marts, weighted
   renewable share, CSV exports and a verified real-data baseline.
- [x] **Offline replay** — rebuild from a recorded manifest, validating its checksum and
   keeping replay time distinct from original retrieval time.
- [x] **Revision tracking** — compare each window before replacement, record separate
   technology/total change counts and prior retrieval IDs, and print an audit summary
   for live and replay loads. Data and audit commit or roll back together.
- [x] **Historical analysis** — extend the baseline to multiple complete years; interpret
   seasonal changes and comparable periods without mixing incomplete months.
   The executed [2024–2025 report](../reports/history-2024-2025.md) covers 731
   consecutive days, 24 complete months and 8,214 observations. All 231 active
   manifests reproduce the source tables, CSVs and report exactly; see the
   [completion evidence](../reports/history-2025-q4-completion.md). Sparse source
   series were recovered only through explicit daily requests under unchanged
   validation, with no imputation.
- [x] **Offline web dashboard: overview** — generate a portable HTML report with
   a year selector, weighted KPIs, monthly generation bars, accessible value tables
   and selected-period source evidence. Use the existing completeness and quality
   gates; keep the warehouse read-only and replace the HTML atomically.
- [x] **Web dashboard: technology breakdown** — show monthly technology contributions
   with source IDs, renewable classification and observed-day coverage. Do not treat
   absent technology observations as measured zeros or add the published total as a
   technology. Filters and reconciliation are verified against SQL; see the
   [executed synthetic and browser checks](../reports/dashboard-technology-verification.md).
- [ ] **Web dashboard: comparable periods** — expose same-calendar-month YoY changes,
   daily averages for leap-year comparisons and percentage-point share changes.
   Verify displayed values and filtered source evidence against the historical report.
- [ ] **Web dashboard: portfolio delivery** — add verified desktop/mobile screenshots,
   a portable example with attribution and instructions for opening the report.
   Check keyboard access and offline interaction before marking delivery complete.

Power BI is an **optional future extension**, outside the active milestones. It may
be resumed only with an environment that can build, open and verify the real report.
A specification or unverified PBIP is not a finished Power BI implementation.

Scheduled work must inspect the current branch and roadmap, work on useful small
tasks, run their relevant checks and commit only verified improvements. No empty
commits, manufactured dates, churn or fabricated analytical findings. If blocked,
report the blocker and leave the current working version intact.
