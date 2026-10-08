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
- [ ] **Historical analysis** — extend the baseline to multiple complete years; interpret
   seasonal changes and comparable periods without mixing incomplete months.
   The report command and offline completeness/comparison tests are implemented.
   Explicit daily request windows recovered the sparse March 2024 response with
   unchanged validation and verified offline replay; see the
   [recovery evidence](../reports/march-2024-daily-recovery.md).
   [Q1–Q3 2024 is validated](../reports/baseline-2024-q1-q3.md): 274 days,
   nine complete months and 3,018 observations, with energy-weighted quarterly
   comparisons. August and September daily recovery matches the monthly source;
   all 127 active manifests reproduce the warehouse and CSVs offline. Load and
   verify the remaining October 2024–December 2025 windows, investigate any
   further sparse responses, and
   execute the complete real-data report before checking this milestone off.
- [ ] **Power BI** — import the exported daily and monthly tables, define measures and
   build and actually verify a compact report. A specification is not a finished PBIX.

Scheduled work must inspect the current branch and roadmap, complete one useful
task, run its relevant checks and commit only a verified improvement. No empty
commits, manufactured dates, churn or fabricated analytical findings. If blocked,
report the blocker and leave the current working version intact.
