-- =============================================================================
-- Mileage vs Grade Correlation
-- Purpose: Relationship between odometer reading and condition grade.
-- Uses CTE + correlation grouping by mileage bucket.
-- =============================================================================

USE vehicle_analytics;

WITH latest AS (
    SELECT f.mileage, f.grade, f.mileage_bucket, f.model
    FROM fct_vehicle_inventory f
    JOIN dim_inventory_snapshot s ON f.snapshot_key = s.snapshot_key
    WHERE s.snapshot_date = (SELECT MAX(snapshot_date) FROM dim_inventory_snapshot)
      AND f.grade IS NOT NULL
)
SELECT
    mileage_bucket,
    COUNT(*)                    AS vehicle_count,
    ROUND(AVG(mileage), 0)      AS avg_mileage,
    ROUND(AVG(grade), 2)        AS avg_grade,
    ROUND(MIN(grade), 2)        AS min_grade,
    ROUND(MAX(grade), 2)        AS max_grade,
    ROUND(STDDEV(grade), 2)     AS grade_stddev
FROM latest
GROUP BY mileage_bucket
ORDER BY FIELD(mileage_bucket, 'LOW', 'MEDIUM', 'HIGH', 'ANOMALY');

-- Pearson-style segment: high mileage vs low mileage grade comparison
SELECT
    CASE WHEN mileage >= 100000 THEN 'High Mileage (100k+)'
         WHEN mileage < 30000  THEN 'Low Mileage (<30k)'
         ELSE 'Mid Mileage' END  AS mileage_segment,
    COUNT(*) AS n,
    ROUND(AVG(grade), 2) AS avg_grade
FROM latest
GROUP BY 1;
