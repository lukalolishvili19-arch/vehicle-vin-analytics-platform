-- =============================================================================
-- 006_create_audit.sql
-- Pipeline audit and data quality tracking
-- =============================================================================

USE vehicle_analytics;

CREATE TABLE IF NOT EXISTS audit_pipeline_run (
    run_id                  BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    pipeline_name           VARCHAR(100)     NOT NULL,
    batch_id                VARCHAR(50)      NOT NULL,
    source_file             VARCHAR(255)     NOT NULL,
    status                  ENUM('RUNNING','SUCCESS','FAILED','PARTIAL') NOT NULL,
    started_at              TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at             TIMESTAMP        NULL,
    rows_extracted          INT UNSIGNED     NULL,
    rows_validated          INT UNSIGNED     NULL,
    rows_quarantined        INT UNSIGNED     NULL,
    rows_loaded             INT UNSIGNED     NULL,
    error_message           TEXT             NULL,

    PRIMARY KEY (run_id),
    INDEX idx_batch (batch_id),
    INDEX idx_status (status),
    INDEX idx_started (started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS audit_data_quality (
    quality_id              BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
    run_id                  BIGINT UNSIGNED  NOT NULL,
    check_name              VARCHAR(100)     NOT NULL,
    check_type              ENUM('SCHEMA','BUSINESS','UNIQUENESS','COMPLETENESS') NOT NULL,
    column_name             VARCHAR(100)     NULL,
    expected_value          VARCHAR(255)     NULL,
    actual_value            VARCHAR(255)     NULL,
    rows_affected           INT UNSIGNED     NOT NULL DEFAULT 0,
    severity                ENUM('INFO','WARNING','ERROR') NOT NULL,
    checked_at              TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (quality_id),
    INDEX idx_run (run_id),
    INDEX idx_check (check_name),
    INDEX idx_severity (severity),

    CONSTRAINT fk_quality_run
        FOREIGN KEY (run_id) REFERENCES audit_pipeline_run (run_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
