-- =============================================================================
-- Top Vehicles by Grade (Ranking)
-- Purpose: Best-condition units available in current inventory snapshot.
-- =============================================================================

USE vehicle_analytics;

WITH latest AS (
    SELECT f.*, al.light_name
    FROM fct_vehicle_inventory f
    JOIN dim_auction_light al ON f.primary_light_key = al.light_key
    JOIN dim_inventory_snapshot s ON f.snapshot_key = s.snapshot_key
    WHERE s.snapshot_date = (SELECT MAX(snapshot_date) FROM dim_inventory_snapshot)
      AND f.grade IS NOT NULL
)
SELECT * FROM (
    SELECT
        vin,
        stock_number,
        model,
        model_year,
        style,
        mileage,
        grade,
        grade_tier,
        light_name,
        has_condition_report,
        ROW_NUMBER() OVER (ORDER BY grade DESC, mileage ASC) AS quality_rank
    FROM latest
) ranked
WHERE quality_rank <= 25
ORDER BY quality_rank;
