-- The API's total lives separately, so it cannot inflate the technology sum.
CREATE OR REPLACE VIEW daily_mix AS
WITH daily AS (
    SELECT region, day,
           SUM(energy_mwh) AS generation_mwh,
           SUM(CASE WHEN renewable THEN energy_mwh ELSE 0 END) AS renewable_mwh,
           SUM(CASE WHEN NOT renewable THEN energy_mwh ELSE 0 END) AS non_renewable_mwh,
           COUNT(*) AS technology_count
    FROM generation
    GROUP BY region, day
)
SELECT d.*, d.renewable_mwh / NULLIF(d.generation_mwh, 0) AS renewable_share,
       t.total_mwh AS source_total_mwh,
       d.generation_mwh - t.total_mwh AS reconciliation_difference_mwh,
       r.source_updated_at, r.retrieved_at, r.sha256 AS source_sha256
FROM daily d
JOIN source_totals t USING (region, day)
JOIN ingestion_runs r ON r.retrieval_id = t.retrieval_id;

-- A month's share is energy-weighted, not an unweighted average of daily shares.
CREATE OR REPLACE VIEW monthly_mix AS
SELECT region, CAST(DATE_TRUNC('month', day) AS DATE) AS month,
       COUNT(*) AS days_observed,
       DAY(LAST_DAY(MIN(day))) AS days_in_month,
       COUNT(*) = DAY(LAST_DAY(MIN(day))) AS is_complete_month,
       SUM(generation_mwh) AS generation_mwh,
       SUM(renewable_mwh) AS renewable_mwh,
       SUM(non_renewable_mwh) AS non_renewable_mwh,
       SUM(renewable_mwh) / NULLIF(SUM(generation_mwh), 0) AS renewable_share,
       MAX(source_updated_at) AS latest_source_update,
       MAX(retrieved_at) AS latest_retrieval
FROM daily_mix
GROUP BY region, DATE_TRUNC('month', day);

CREATE OR REPLACE VIEW monthly_technology AS
SELECT region, CAST(DATE_TRUNC('month', day) AS DATE) AS month,
       technology_id, technology, renewable,
       COUNT(*) AS days_observed,
       SUM(energy_mwh) AS generation_mwh
FROM generation
GROUP BY region, DATE_TRUNC('month', day), technology_id, technology, renewable;
