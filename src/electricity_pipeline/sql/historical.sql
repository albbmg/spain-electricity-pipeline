-- Restrict the analysis before aggregating; unrelated loaded dates stay out.
WITH selected AS (
    SELECT day, generation_mwh, renewable_mwh
    FROM daily_mix
    WHERE region = ? AND day BETWEEN ? AND ?
), periods AS (
    SELECT 'year' AS grain, CAST(DATE_TRUNC('year', day) AS DATE) AS period_start,
           generation_mwh, renewable_mwh FROM selected
    UNION ALL
    SELECT 'quarter', CAST(DATE_TRUNC('quarter', day) AS DATE),
           generation_mwh, renewable_mwh FROM selected
    UNION ALL
    SELECT 'month', CAST(DATE_TRUNC('month', day) AS DATE),
           generation_mwh, renewable_mwh FROM selected
)
SELECT grain, period_start, COUNT(*) AS days_observed,
       DATE_DIFF('day', period_start, CASE grain
           WHEN 'year' THEN period_start + INTERVAL '1 year'
           WHEN 'quarter' THEN period_start + INTERVAL '3 months'
           ELSE period_start + INTERVAL '1 month'
       END) AS days_expected,
       SUM(generation_mwh) AS generation_mwh,
       SUM(renewable_mwh) AS renewable_mwh
FROM periods
GROUP BY grain, period_start
ORDER BY grain, period_start;
