-- =============================================================================
-- Condition Report & Grade Coverage
-- Purpose: Data completeness and quality segmentation for buyers.
-- =============================================================================

USE vehicle_analytics;

WITH latest AS (
    SELECT f.*
    FROM fct_vehicle_inventory f
    JOIN dim_inventory_snapshot s ON f.snapshot_key = s.snapshot_key
    WHERE s.snapshot_date = (SELECT MAX(snapshot_date) FROM dim_inventory_snapshot)
)
SELECT
    has_condition_report,
    COUNT(*) AS vehicle_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct,
    SUM(CASE WHEN grade IS NULL THEN 1 ELSE 0 END) AS missing_grade,
    ROUND(AVG(grade), 2) AS avg_grade_when_present
FROM latest
GROUP BY has_condition_report;

-- Model-level coverage
SELECT
    model,
    COUNT(*) AS total,
    SUM(has_condition_report) AS with_report,
    ROUND(100.0 * SUM(has_condition_report) / COUNT(*), 1) AS report_pct,
    ROUND(AVG(grade), 2) AS avg_grade
FROM latest
GROUP BY model
ORDER BY total DESC;
