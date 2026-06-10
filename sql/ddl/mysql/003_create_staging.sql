-- =============================================================================
-- 003_create_staging.sql
-- Staging tables — mirror of source CSV with ETL audit columns
-- =============================================================================

USE vehicle_analytics;

CREATE TABLE IF NOT EXISTS stg_vehicle_search (
    stg_id                  BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,

    -- Source columns (exact CSV mapping)
    picture_count           SMALLINT UNSIGNED NULL,
    stock_number            VARCHAR(20)      NOT NULL,
    model_year              SMALLINT UNSIGNED NOT NULL,
    make                    VARCHAR(50)      NOT NULL,
    model                   VARCHAR(100)     NOT NULL,
    style                   VARCHAR(150)     NULL,
    exterior_color          VARCHAR(50)      NOT NULL,
    mileage                 INT UNSIGNED     NOT NULL,
    has_condition_report    TINYINT(1)       NOT NULL DEFAULT 0,
    grade                   DECIMAL(3,1)     NULL,
    lights_raw              VARCHAR(100)     NULL,
    announcements           TEXT             NULL,
    vin                     CHAR(17)         NOT NULL,

    -- ETL audit columns
    source_file             VARCHAR(255)     NOT NULL,
    batch_id                VARCHAR(50)      NOT NULL,
    ingested_at             TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_valid                TINYINT(1)       NOT NULL DEFAULT 1,
    validation_errors       JSON             NULL,

    PRIMARY KEY (stg_id),
    INDEX idx_stg_vin (vin),
    INDEX idx_stg_stock (stock_number),
    INDEX idx_stg_batch (batch_id),
    INDEX idx_stg_valid (is_valid)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Quarantine: rejected rows from staging validation
CREATE TABLE IF NOT EXISTS stg_vehicle_search_quarantine (
    quarantine_id           BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,

    -- Original row data (same as staging)
    picture_count           SMALLINT UNSIGNED NULL,
    stock_number            VARCHAR(20)      NULL,
    model_year              SMALLINT UNSIGNED NULL,
    make                    VARCHAR(50)      NULL,
    model                   VARCHAR(100)     NULL,
    style                   VARCHAR(150)     NULL,
    exterior_color          VARCHAR(50)      NULL,
    mileage                 INT UNSIGNED     NULL,
    has_condition_report    TINYINT(1)       NULL,
    grade                   DECIMAL(3,1)     NULL,
    lights_raw              VARCHAR(100)     NULL,
    announcements           TEXT             NULL,
    vin                     VARCHAR(20)      NULL,

    -- Quarantine metadata
    rejection_reason        VARCHAR(255)     NOT NULL,
    rejection_code          VARCHAR(50)      NOT NULL,
    source_file             VARCHAR(255)     NOT NULL,
    batch_id                VARCHAR(50)      NOT NULL,
    quarantined_at          TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (quarantine_id),
    INDEX idx_quarantine_batch (batch_id),
    INDEX idx_quarantine_code (rejection_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
