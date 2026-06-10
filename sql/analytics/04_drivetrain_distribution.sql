-- =============================================================================
-- Drivetrain Distribution (derived from Style field)
-- Purpose: AWD vs RWD share — proxy for "transmission/drivetrain" analysis.
-- Source: Style contains xDrive, sDrive, etc. (stored in gold/ETL as drivetrain_type)
-- =============================================================================

USE vehicle_analytics;

-- If drivetrain not yet in warehouse, parse from style at query time:
WITH latest AS (
    SELECT
        f.style,
        f.model,
        CASE
            WHEN UPPER(f.style) LIKE '%XDRIVE%' OR UPPER(f.style) LIKE '%XI%' THEN 'AWD'
            WHEN UPPER(f.style) LIKE '%SDRIVE%' THEN 'RWD'
            ELSE 'UNKNOWN'
        END AS drivetrain_type
    FROM fct_vehicle_inventory f
    JOIN dim_inventory_snapshot s ON f.snapshot_key = s.snapshot_key
    WHERE s.snapshot_date = (SELECT MAX(snapshot_date) FROM dim_inventory_snapshot)
)
SELECT
    drivetrain_type,
    COUNT(*) AS vehicle_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_fleet
FROM latest
GROUP BY drivetrain_type
ORDER BY vehicle_count DESC;

-- By model
SELECT
    model,
    drivetrain_type,
    COUNT(*) AS cnt
FROM latest
WHERE drivetrain_type != 'UNKNOWN'
GROUP BY model, drivetrain_type
ORDER BY model, cnt DESC;
