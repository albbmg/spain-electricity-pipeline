-- Every check returns zero violations. Queries also work on a partially built history.
SELECT 'total_reconciliation' AS check_name, COUNT(*) AS violations
FROM daily_mix
WHERE ABS(reconciliation_difference_mwh) > GREATEST(0.1, source_total_mwh * 0.000001)
UNION ALL
SELECT 'daily_energy_split', COUNT(*) FROM daily_mix
WHERE generation_mwh <> renewable_mwh + non_renewable_mwh
UNION ALL
SELECT 'bounded_renewable_share', COUNT(*) FROM daily_mix
WHERE renewable_share IS NULL OR renewable_share < 0 OR renewable_share > 1
UNION ALL
SELECT 'orphan_generation_date', COUNT(*) FROM generation g
LEFT JOIN source_totals t USING (region, day) WHERE t.day IS NULL
UNION ALL
SELECT 'orphan_source_total', COUNT(*) FROM source_totals t
LEFT JOIN generation g USING (region, day) WHERE g.day IS NULL
UNION ALL
SELECT 'missing_observation_lineage', COUNT(*) FROM generation g
LEFT JOIN ingestion_runs r USING (retrieval_id) WHERE r.retrieval_id IS NULL
UNION ALL
SELECT 'missing_total_lineage', COUNT(*) FROM source_totals t
LEFT JOIN ingestion_runs r USING (retrieval_id) WHERE r.retrieval_id IS NULL
UNION ALL
SELECT 'observation_outside_source_window', COUNT(*) FROM generation g
JOIN ingestion_runs r USING (retrieval_id)
WHERE g.day NOT BETWEEN r.start_date AND r.end_date OR g.region <> r.region
UNION ALL
SELECT 'mismatched_daily_lineage', COUNT(*) FROM generation g
JOIN source_totals t USING (region, day) WHERE g.retrieval_id <> t.retrieval_id;
