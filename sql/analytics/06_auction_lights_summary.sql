-- =============================================================================
-- Auction Lights Summary
-- Purpose: Risk signal distribution (Green vs Red vs Yellow).
-- =============================================================================

USE vehicle_analytics;

WITH latest AS (
    SELECT f.inventory_key, al.light_name
    FROM fct_vehicle_inventory f
    JOIN bridge_vehicle_lights b ON f.inventory_key = b.inventory_key
    JOIN dim_auction_light al ON b.light_key = al.light_key
    JOIN dim_inventory_snapshot s ON f.snapshot_key = s.snapshot_key
    WHERE s.snapshot_date = (SELECT MAX(snapshot_date) FROM dim_inventory_snapshot)
)
SELECT
    light_name,
    COUNT(DISTINCT inventory_key) AS vehicles,
    ROUND(100.0 * COUNT(DISTINCT inventory_key) /
        (SELECT COUNT(*) FROM fct_vehicle_inventory fi
         JOIN dim_inventory_snapshot si ON fi.snapshot_key = si.snapshot_key
         WHERE si.snapshot_date = (SELECT MAX(snapshot_date) FROM dim_inventory_snapshot)), 2)
    AS pct_of_fleet
FROM latest
GROUP BY light_name
ORDER BY vehicles DESC;
