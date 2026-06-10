-- =============================================================================
-- Inventory KPI Dashboard Query
-- Purpose: Single-row executive metrics for BI tools (Power BI / Metabase).
-- =============================================================================

USE vehicle_analytics;

WITH latest AS (
    SELECT f.*
    FROM fct_vehicle_inventory f
    JOIN dim_inventory_snapshot s ON f.snapshot_key = s.snapshot_key
    WHERE s.snapshot_date = (SELECT MAX(snapshot_date) FROM dim_inventory_snapshot)
)
SELECT
    COUNT(*)                                    AS total_vehicles,
    COUNT(DISTINCT model)                       AS total_models,
    COUNT(DISTINCT make)                        AS total_makes,
    ROUND(AVG(mileage), 0)                      AS avg_mileage,
    ROUND(AVG(grade), 2)                        AS avg_grade,
    SUM(has_condition_report)                   AS with_condition_report,
    ROUND(100.0 * SUM(has_condition_report) / COUNT(*), 1) AS condition_report_pct,
    SUM(is_as_is)                               AS as_is_count,
    SUM(has_structural_damage)                  AS structural_count,
    SUM(CASE WHEN grade >= 4.5 THEN 1 ELSE 0 END) AS excellent_grade_count,
    SUM(CASE WHEN mileage_bucket = 'HIGH' THEN 1 ELSE 0 END) AS high_mileage_count,
    AVG(picture_count)                          AS avg_picture_count
FROM latest;
