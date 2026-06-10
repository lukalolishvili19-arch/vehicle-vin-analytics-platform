-- =============================================================================
-- 007_create_views.sql
-- BI-facing analytical views
-- =============================================================================

USE vehicle_analytics;

-- Current inventory (latest snapshot only)
CREATE OR REPLACE VIEW vw_vehicle_inventory_current AS
SELECT
    f.inventory_key,
    f.vin,
    f.stock_number,
    f.model_year,
    f.make,
    f.model,
    f.style,
    f.exterior_color,
    f.picture_count,
    f.mileage,
    f.mileage_bucket,
    f.vehicle_age,
    f.has_condition_report,
    f.grade,
    f.grade_tier,
    al.light_name              AS primary_light,
    f.lights_raw,
    f.has_multiple_lights,
    f.is_as_is,
    f.is_inop,
    f.has_structural_damage,
    f.is_salvage,
    f.is_repo,
    f.is_green_light,
    f.announcements,
    s.snapshot_date,
    f.loaded_at
FROM fct_vehicle_inventory f
JOIN dim_inventory_snapshot s  ON f.snapshot_key = s.snapshot_key
JOIN dim_auction_light al      ON f.primary_light_key = al.light_key
WHERE s.snapshot_date = (
    SELECT MAX(snapshot_date) FROM dim_inventory_snapshot
);

-- Inventory summary by model
CREATE OR REPLACE VIEW vw_inventory_by_model AS
SELECT
    f.make,
    f.model,
    COUNT(*)                                    AS vehicle_count,
    ROUND(AVG(f.mileage), 0)                   AS avg_mileage,
    ROUND(AVG(f.grade), 2)                     AS avg_grade,
    SUM(f.has_condition_report)                 AS with_condition_report,
    ROUND(100.0 * SUM(f.has_condition_report) / COUNT(*), 1)
                                                AS condition_report_pct,
    SUM(f.is_as_is)                             AS as_is_count,
    SUM(f.has_structural_damage)                AS structural_damage_count
FROM fct_vehicle_inventory f
JOIN dim_inventory_snapshot s ON f.snapshot_key = s.snapshot_key
WHERE s.snapshot_date = (SELECT MAX(snapshot_date) FROM dim_inventory_snapshot)
GROUP BY f.make, f.model
ORDER BY vehicle_count DESC;

-- Auction lights distribution
CREATE OR REPLACE VIEW vw_auction_lights_summary AS
SELECT
    al.light_name,
    COUNT(DISTINCT f.inventory_key)             AS vehicle_count,
    ROUND(100.0 * COUNT(DISTINCT f.inventory_key) /
        (SELECT COUNT(*) FROM fct_vehicle_inventory fi
         JOIN dim_inventory_snapshot si ON fi.snapshot_key = si.snapshot_key
         WHERE si.snapshot_date = (SELECT MAX(snapshot_date) FROM dim_inventory_snapshot)), 1)
                                                AS pct_of_fleet
FROM fct_vehicle_inventory f
JOIN bridge_vehicle_lights b   ON f.inventory_key = b.inventory_key
JOIN dim_auction_light al      ON b.light_key = al.light_key
JOIN dim_inventory_snapshot s  ON f.snapshot_key = s.snapshot_key
WHERE s.snapshot_date = (SELECT MAX(snapshot_date) FROM dim_inventory_snapshot)
GROUP BY al.light_name
ORDER BY vehicle_count DESC;

-- Grade distribution by model year
CREATE OR REPLACE VIEW vw_grade_by_year AS
SELECT
    f.model_year,
    COUNT(*)                                    AS vehicle_count,
    ROUND(AVG(f.grade), 2)                     AS avg_grade,
    MIN(f.grade)                                AS min_grade,
    MAX(f.grade)                                AS max_grade,
    SUM(CASE WHEN f.grade >= 4.5 THEN 1 ELSE 0 END) AS excellent_count,
    SUM(CASE WHEN f.grade < 2.5  THEN 1 ELSE 0 END) AS poor_count
FROM fct_vehicle_inventory f
JOIN dim_inventory_snapshot s ON f.snapshot_key = s.snapshot_key
WHERE s.snapshot_date = (SELECT MAX(snapshot_date) FROM dim_inventory_snapshot)
  AND f.grade IS NOT NULL
GROUP BY f.model_year
ORDER BY f.model_year DESC;

-- Condition report coverage
CREATE OR REPLACE VIEW vw_condition_report_coverage AS
SELECT
    f.model,
    COUNT(*)                                    AS total,
    SUM(f.has_condition_report)                 AS with_report,
    SUM(CASE WHEN f.has_condition_report = 0 THEN 1 ELSE 0 END) AS without_report,
    ROUND(100.0 * SUM(f.has_condition_report) / COUNT(*), 1) AS coverage_pct,
    SUM(CASE WHEN f.has_condition_report = 1 AND f.grade IS NULL THEN 1 ELSE 0 END)
                                                AS report_without_grade
FROM fct_vehicle_inventory f
JOIN dim_inventory_snapshot s ON f.snapshot_key = s.snapshot_key
WHERE s.snapshot_date = (SELECT MAX(snapshot_date) FROM dim_inventory_snapshot)
GROUP BY f.model
ORDER BY total DESC;
