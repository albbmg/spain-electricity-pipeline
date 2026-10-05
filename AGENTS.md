# Working on this project

- Read README.md, docs/source-contract.md and docs/roadmap.md before changing behaviour.
- Work in small coherent increments with real, verified improvements. Update the
  roadmap when a milestone is actually complete. Avoid empty commits and cosmetic churn.
- Keep the focus on reproducible API ingestion, data quality and analytical SQL.
- Preserve the explicit peninsular geography, Europe/Madrid date semantics and
  separation of technology observations from published totals.
- Never silently impute missing measurements or reinterpret unknown categories.
- Preserve raw source evidence and the transactional replacement boundary. Do not
  clear existing user data to make a failing run succeed.
- Mark synthetic examples clearly. Attribute real-data outputs to Red Eléctrica,
  retain update/retrieval dates, and keep claims within the observed period.
- Do not commit raw downloads, databases, virtual environments, credentials or
  employer/client data. MIT applies to project code, not third-party source data.
- Run ruff check ., ruff format --check . and relevant pytest tests before a commit.
  Verify live extraction only when a change needs it; routine CI must work offline.
- Read current remote state before publishing. Never force-push or overwrite
  concurrent changes. Report blockers honestly; do not claim a remote commit or
  completed Power BI report without verifying it.
- The README and technical documentation are in English. Keep prose concrete and
  professional; do not add recruiting claims, unverifiable experience or marketing filler.
