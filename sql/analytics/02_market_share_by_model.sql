-- =============================================================================
-- Market Share by Model
-- Purpose: Inventory share per BMW model line using window functions.
-- =============================================================================

USE vehicle_analytics;

WITH latest AS (
    SELECT f.*
    FROM fct_vehicle_inventory f
    JOIN dim_inventory_snapshot s ON f.snapshot_key = s.snapshot_key
    WHERE s.snapshot_date = (SELECT MAX(snapshot_date) FROM dim_inventory_snapshot)
),
totals AS (
    SELECT COUNT(*) AS fleet_total FROM latest
)
SELECT
    l.model,
    COUNT(*)                                              AS vehicle_count,
    ROUND(100.0 * COUNT(*) / t.fleet_total, 2)           AS pct_of_fleet,
    RANK() OVER (ORDER BY COUNT(*) DESC)                 AS model_rank,
    ROUND(AVG(l.mileage), 0)                             AS avg_mileage,
    ROUND(AVG(l.grade), 2)                               AS avg_grade
FROM latest l
CROSS JOIN totals t
GROUP BY l.model, t.fleet_total
ORDER BY vehicle_count DESC;
