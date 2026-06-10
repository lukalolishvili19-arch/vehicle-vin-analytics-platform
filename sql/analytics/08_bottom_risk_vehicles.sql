-- =============================================================================
-- Bottom / High-Risk Vehicles (Ranking)
-- Purpose: Lowest grade and highest-risk flags for due diligence.
-- =============================================================================

USE vehicle_analytics;

WITH latest AS (
    SELECT f.*, al.light_name
    FROM fct_vehicle_inventory f
    JOIN dim_auction_light al ON f.primary_light_key = al.light_key
    JOIN dim_inventory_snapshot s ON f.snapshot_key = s.snapshot_key
    WHERE s.snapshot_date = (SELECT MAX(snapshot_date) FROM dim_inventory_snapshot)
)
SELECT
    vin,
    stock_number,
    model,
    model_year,
    mileage,
    COALESCE(grade, 0) AS grade,
    light_name,
    is_as_is,
    has_structural_damage,
    is_salvage,
    is_inop,
    announcements,
    ROW_NUMBER() OVER (
        ORDER BY
            COALESCE(grade, 0) ASC,
            is_as_is DESC,
            has_structural_damage DESC
    ) AS risk_rank
FROM latest
WHERE is_as_is = 1 OR has_structural_damage = 1 OR grade < 2.0 OR is_inop = 1
ORDER BY risk_rank
LIMIT 30;
