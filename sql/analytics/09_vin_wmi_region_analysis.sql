-- =============================================================================
-- VIN WMI Region Analysis
-- Purpose: Geographic origin proxy from VIN World Manufacturer Identifier.
-- Note: True dealer geography is NOT in dataset; WMI indicates build region.
-- =============================================================================

USE vehicle_analytics;

WITH latest AS (
    SELECT
        f.vin,
        f.model,
        LEFT(f.vin, 3) AS wmi_prefix,
        f.grade,
        f.mileage
    FROM fct_vehicle_inventory f
    JOIN dim_inventory_snapshot s ON f.snapshot_key = s.snapshot_key
    WHERE s.snapshot_date = (SELECT MAX(snapshot_date) FROM dim_inventory_snapshot)
)
SELECT
    l.wmi_prefix,
    COALESCE(r.region, 'Unknown') AS build_region,
    COALESCE(r.manufacturer, 'Unknown') AS manufacturer,
    COUNT(*) AS vehicle_count,
    ROUND(AVG(l.grade), 2) AS avg_grade,
    ROUND(AVG(l.mileage), 0) AS avg_mileage
FROM latest l
LEFT JOIN ref_vin_wmi r ON l.wmi_prefix = r.wmi_prefix
GROUP BY l.wmi_prefix, r.region, r.manufacturer
ORDER BY vehicle_count DESC;
