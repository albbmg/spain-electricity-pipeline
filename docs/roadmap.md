# Small, verifiable milestones

Work one coherent change at a time. A milestone is complete only after execution
and verification; a plan or specification is not an implemented feature.

1. **Source contract** — define geography, grain, units, failure rules and questions.
2. **Acquisition and validation** — bounded requests, retry policy, raw evidence,
   completeness checks, total reconciliation and tests with explicitly synthetic data.
3. **Analytical storage** — transactional window replacement, SQL marts, weighted
   renewable share, CSV exports and a verified real-data baseline.
4. **Offline replay** — rebuild from a recorded manifest, validating its checksum and
   keeping replay time distinct from original retrieval time.
5. **Revision tracking** — compare repeat loads, quantify added/changed/removed rows
   and provide a useful audit summary.
6. **Historical analysis** — extend the baseline to multiple complete years; interpret
   seasonal changes and comparable periods without mixing incomplete months.
7. **Power BI** — import the exported daily and monthly tables, define measures and
   build and actually verify a compact report. A specification is not a finished PBIX.

Scheduled work must inspect the current branch and roadmap, complete one useful
task, run its relevant checks and commit only a verified improvement. No empty
commits, manufactured dates, churn or fabricated analytical findings. If blocked,
report the blocker and leave the current working version intact.
