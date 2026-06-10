-- =============================================================================
-- 004_create_dimensions.sql
-- Dimension tables for star schema
-- =============================================================================

USE vehicle_analytics;

-- ---------------------------------------------------------------------------
-- dim_inventory_snapshot — one row per pipeline load / inventory snapshot date
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_inventory_snapshot (
    snapshot_key            INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    snapshot_date           DATE             NOT NULL,
    source_file             VARCHAR(255)     NOT NULL,
    batch_id                VARCHAR(50)      NOT NULL,
    total_records           INT UNSIGNED     NOT NULL DEFAULT 0,
    valid_records           INT UNSIGNED     NOT NULL DEFAULT 0,
    quarantined_records     INT UNSIGNED     NOT NULL DEFAULT 0,
    loaded_at               TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (snapshot_key),
    UNIQUE KEY uq_snapshot_date_file (snapshot_date, source_file),
    INDEX idx_snapshot_date (snapshot_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- dim_make_model — vehicle make / model hierarchy
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_make_model (
    make_model_key          INT UNSIGNED     NOT NULL AUTO_INCREMENT,
    make                    VARCHAR(50)      NOT NULL,
    model                   VARCHAR(100)     NOT NULL,
    model_series            VARCHAR(20)      NULL COMMENT 'Derived series: 2, 3, 5, X, i, M',
    is_electric             TINYINT(1)       NOT NULL DEFAULT 0,
    is_m_series             TINYINT(1)       NOT NULL DEFAULT 0,
    created_at              TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                               ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (make_model_key),
    UNIQUE KEY uq_make_model (make, model),
    INDEX idx_make (make),
    INDEX idx_model (model)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- dim_exterior_color — standardized color lookup
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_exterior_color (
    color_key               SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    color_name              VARCHAR(50)      NOT NULL,
    color_name_normalized   VARCHAR(50)      NOT NULL,

    PRIMARY KEY (color_key),
    UNIQUE KEY uq_color_name (color_name_normalized)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Seed known colors from dataset
INSERT INTO dim_exterior_color (color_name, color_name_normalized) VALUES
    ('BLACK',  'BLACK'),
    ('WHITE',  'WHITE'),
    ('GRAY',   'GRAY'),
    ('BLUE',   'BLUE'),
    ('SILVER', 'SILVER'),
    ('RED',    'RED'),
    ('BROWN',  'BROWN'),
    ('ORANGE', 'ORANGE'),
    ('GREEN',  'GREEN'),
    ('GOLD',   'GOLD'),
    ('BEIGE',  'BEIGE'),
    ('PINK',   'PINK'),
    ('TEAL',   'TEAL'),
    ('TAN',    'TAN'),
    ('GY',     'GRAY'),
    ('SV',     'SILVER'),
    ('BL',     'BLUE'),
    ('NO COLOR', 'UNKNOWN')
ON DUPLICATE KEY UPDATE color_name = VALUES(color_name);

-- ---------------------------------------------------------------------------
-- dim_auction_light — auction signal light dimension
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_auction_light (
    light_key               TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
    light_code              VARCHAR(20)      NOT NULL,
    light_name              VARCHAR(50)      NOT NULL,

    PRIMARY KEY (light_key),
    UNIQUE KEY uq_light_code (light_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO dim_auction_light (light_code, light_name) VALUES
    ('RED',     'Red'),
    ('GREEN',   'Green'),
    ('YELLOW',  'Yellow'),
    ('WHITE',   'White'),
    ('BLUE',    'Blue'),
    ('UNKNOWN', 'Unknown')
ON DUPLICATE KEY UPDATE light_name = VALUES(light_name);

-- ---------------------------------------------------------------------------
-- dim_vehicle — SCD Type 2 vehicle dimension (VIN as natural key)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS dim_vehicle (
    vehicle_key             BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    vin                     CHAR(17)         NOT NULL,
    stock_number            VARCHAR(20)      NOT NULL,

    -- Foreign keys to other dimensions
    make_model_key          INT UNSIGNED     NOT NULL,
    color_key               SMALLINT UNSIGNED NOT NULL,

    -- Vehicle attributes (may change over time → SCD2)
    model_year              SMALLINT UNSIGNED NOT NULL,
    style                   VARCHAR(150)     NULL,
    wmi_prefix              CHAR(3)          NULL COMMENT 'First 3 chars of VIN',
    vin_region              VARCHAR(50)      NULL COMMENT 'Derived from WMI lookup',

    -- SCD Type 2 columns
    effective_from          DATE             NOT NULL,
    effective_to            DATE             NOT NULL DEFAULT '9999-12-31',
    is_current              TINYINT(1)       NOT NULL DEFAULT 1,

    -- Audit
    created_at              TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                               ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (vehicle_key),
    UNIQUE KEY uq_vin_effective (vin, effective_from),
    INDEX idx_vin_current (vin, is_current),
    INDEX idx_stock_number (stock_number),
    INDEX idx_model_year (model_year),
    INDEX idx_make_model (make_model_key),

    CONSTRAINT fk_vehicle_make_model
        FOREIGN KEY (make_model_key) REFERENCES dim_make_model (make_model_key),
    CONSTRAINT fk_vehicle_color
        FOREIGN KEY (color_key) REFERENCES dim_exterior_color (color_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
