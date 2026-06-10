-- =============================================================================
-- 005_create_facts.sql
-- Fact tables and bridge tables
-- =============================================================================

USE vehicle_analytics;

-- ---------------------------------------------------------------------------
-- fct_vehicle_inventory — core fact table
-- Grain: one row per vehicle (VIN) per inventory snapshot
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS fct_vehicle_inventory (
    inventory_key           BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,

    -- Dimension foreign keys
    snapshot_key            INT UNSIGNED     NOT NULL,
    vehicle_key             BIGINT UNSIGNED  NOT NULL,
    make_model_key          INT UNSIGNED     NOT NULL,
    color_key               SMALLINT UNSIGNED NOT NULL,
    primary_light_key       TINYINT UNSIGNED NOT NULL,

    -- Degenerate dimensions (for query convenience)
    vin                     CHAR(17)         NOT NULL,
    stock_number            VARCHAR(20)      NOT NULL,
    model_year              SMALLINT UNSIGNED NOT NULL,
    make                    VARCHAR(50)      NOT NULL,
    model                   VARCHAR(100)     NOT NULL,
    style                   VARCHAR(150)     NULL,
    exterior_color          VARCHAR(50)      NOT NULL,

    -- Listing images: count only (no image_url in source CSV)
    picture_count           SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    mileage                 INT UNSIGNED     NOT NULL,
    mileage_bucket          VARCHAR(20)      NOT NULL,
    is_mileage_anomaly      TINYINT(1)       NOT NULL DEFAULT 0,
    vehicle_age             SMALLINT         NOT NULL COMMENT 'snapshot_year - model_year',
    has_condition_report    TINYINT(1)       NOT NULL DEFAULT 0,
    grade                   DECIMAL(3,1)     NULL,
    grade_tier              VARCHAR(20)      NULL,

    -- Announcements (raw + derived flags)
    announcements           TEXT             NULL,
    is_as_is                TINYINT(1)       NOT NULL DEFAULT 0,
    is_inop                 TINYINT(1)       NOT NULL DEFAULT 0,
    has_structural_damage   TINYINT(1)       NOT NULL DEFAULT 0,
    is_salvage              TINYINT(1)       NOT NULL DEFAULT 0,
    is_repo                 TINYINT(1)       NOT NULL DEFAULT 0,
    is_green_light          TINYINT(1)       NOT NULL DEFAULT 0,

    -- Lights (raw value preserved)
    lights_raw              VARCHAR(100)     NULL,
    has_multiple_lights     TINYINT(1)       NOT NULL DEFAULT 0,

    -- Audit
    loaded_at               TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (inventory_key),
    UNIQUE KEY uq_vin_snapshot (vin, snapshot_key),
    INDEX idx_snapshot (snapshot_key),
    INDEX idx_vehicle (vehicle_key),
    INDEX idx_model_year (model_year),
    INDEX idx_make_model (make, model),
    INDEX idx_grade (grade),
    INDEX idx_mileage (mileage),
    INDEX idx_mileage_bucket (mileage_bucket),
    INDEX idx_primary_light (primary_light_key),
    INDEX idx_condition_report (has_condition_report),
    INDEX idx_structural (has_structural_damage),
    INDEX idx_as_is (is_as_is),

    CONSTRAINT fk_fct_snapshot
        FOREIGN KEY (snapshot_key) REFERENCES dim_inventory_snapshot (snapshot_key),
    CONSTRAINT fk_fct_vehicle
        FOREIGN KEY (vehicle_key) REFERENCES dim_vehicle (vehicle_key),
    CONSTRAINT fk_fct_make_model
        FOREIGN KEY (make_model_key) REFERENCES dim_make_model (make_model_key),
    CONSTRAINT fk_fct_color
        FOREIGN KEY (color_key) REFERENCES dim_exterior_color (color_key),
    CONSTRAINT fk_fct_primary_light
        FOREIGN KEY (primary_light_key) REFERENCES dim_auction_light (light_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- bridge_vehicle_lights — many-to-many for multi-value Lights field
-- Handles cases like "Green,Yellow" or "Red,Blue"
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bridge_vehicle_lights (
    bridge_id               BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    inventory_key           BIGINT UNSIGNED  NOT NULL,
    light_key               TINYINT UNSIGNED NOT NULL,
    light_sequence          TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '1=primary, 2+=secondary',
    is_primary              TINYINT(1)       NOT NULL DEFAULT 0,

    PRIMARY KEY (bridge_id),
    UNIQUE KEY uq_inventory_light (inventory_key, light_key),
    INDEX idx_light (light_key),

    CONSTRAINT fk_bridge_inventory
        FOREIGN KEY (inventory_key) REFERENCES fct_vehicle_inventory (inventory_key),
    CONSTRAINT fk_bridge_light
        FOREIGN KEY (light_key) REFERENCES dim_auction_light (light_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
