-- =============================================================================
-- Grade Analysis by Model and Year
-- Purpose: Average auction condition grade by model line and model year.
-- Note: Price is NOT in source data; Grade is the quality proxy.
-- =============================================================================

USE vehicle_analytics;

WITH graded AS (
    SELECT
        f.model,
        f.model_year,
        f.grade,
        f.mileage,
        al.light_name AS primary_light
    FROM fct_vehicle_inventory f
    JOIN dim_auction_light al ON f.primary_light_key = al.light_key
    JOIN dim_inventory_snapshot s ON f.snapshot_key = s.snapshot_key
    WHERE f.grade IS NOT NULL
      AND s.snapshot_date = (SELECT MAX(snapshot_date) FROM dim_inventory_snapshot)
)
SELECT
    model,
    model_year,
    COUNT(*)                    AS vehicle_count,
    ROUND(AVG(grade), 2)       AS avg_grade,
    ROUND(AVG(mileage), 0)      AS avg_mileage,
    MIN(grade)                  AS min_grade,
    MAX(grade)                  AS max_grade
FROM graded
GROUP BY model, model_year
HAVING COUNT(*) >= 3
ORDER BY model, model_year DESC;
