-- Staging tables for ETL loads
-- TODO: Define stg_vehicle_search table

CREATE TABLE IF NOT EXISTS staging.stg_vehicle_search (
    vin VARCHAR(17) PRIMARY KEY
    -- TODO: Add remaining columns
);
