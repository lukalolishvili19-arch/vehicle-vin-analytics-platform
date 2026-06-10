-- =============================================================================
-- 002_create_reference.sql
-- Reference / seed lookup tables
-- =============================================================================

USE vehicle_analytics;

-- Auction light codes (Red, Green, Yellow, White, Blue, Unknown)
CREATE TABLE IF NOT EXISTS ref_auction_light (
    light_code      VARCHAR(20)     NOT NULL,
    light_name      VARCHAR(50)     NOT NULL,
    light_order     TINYINT         NOT NULL DEFAULT 0,
    description     VARCHAR(255)    NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (light_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO ref_auction_light (light_code, light_name, light_order, description) VALUES
    ('RED',     'Red',     1, 'Stop / issue — inspect carefully'),
    ('GREEN',   'Green',   2, 'Clear / ride and drive'),
    ('YELLOW',  'Yellow',  3, 'Caution — limited guarantee or known issue'),
    ('WHITE',   'White',   4, 'Seller guarantee'),
    ('BLUE',    'Blue',    5, 'Special announcement'),
    ('UNKNOWN', 'Unknown', 99, 'Missing or unparseable light value')
ON DUPLICATE KEY UPDATE light_name = VALUES(light_name);

-- VIN World Manufacturer Identifier (WMI) prefix lookup
CREATE TABLE IF NOT EXISTS ref_vin_wmi (
    wmi_prefix      CHAR(3)         NOT NULL,
    region          VARCHAR(50)     NOT NULL,
    manufacturer    VARCHAR(100)    NOT NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (wmi_prefix)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO ref_vin_wmi (wmi_prefix, region, manufacturer) VALUES
    ('WBA', 'Germany', 'BMW AG'),
    ('WBS', 'Germany', 'BMW M GmbH'),
    ('WBX', 'Germany', 'BMW AG'),
    ('WBY', 'Germany', 'BMW AG'),
    ('5UX', 'USA',     'BMW USA'),
    ('5UM', 'USA',     'BMW USA'),
    ('5YM', 'USA',     'BMW USA'),
    ('5UX', 'USA',     'BMW USA'),
    ('WBA', 'Germany', 'BMW AG')
ON DUPLICATE KEY UPDATE manufacturer = VALUES(manufacturer);

-- Mileage bucket reference
CREATE TABLE IF NOT EXISTS ref_mileage_bucket (
    bucket_code     VARCHAR(20)     NOT NULL,
    bucket_label    VARCHAR(50)     NOT NULL,
    min_mileage     INT UNSIGNED    NOT NULL,
    max_mileage     INT UNSIGNED    NULL,
    PRIMARY KEY (bucket_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO ref_mileage_bucket (bucket_code, bucket_label, min_mileage, max_mileage) VALUES
    ('LOW',    'Low (< 30k mi)',       0,     29999),
    ('MEDIUM', 'Medium (30k–100k mi)', 30000, 100000),
    ('HIGH',   'High (> 100k mi)',     100001, NULL),
    ('ANOMALY','Anomaly (0 or 1 mi)',  0,     1)
ON DUPLICATE KEY UPDATE bucket_label = VALUES(bucket_label);

-- Grade tier reference
CREATE TABLE IF NOT EXISTS ref_grade_tier (
    tier_code       VARCHAR(20)     NOT NULL,
    tier_label      VARCHAR(50)     NOT NULL,
    min_grade       DECIMAL(3,1)    NOT NULL,
    max_grade       DECIMAL(3,1)    NOT NULL,
    PRIMARY KEY (tier_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO ref_grade_tier (tier_code, tier_label, min_grade, max_grade) VALUES
    ('EXCELLENT', 'Excellent (4.5–5.0)', 4.5, 5.0),
    ('GOOD',      'Good (3.5–4.4)',      3.5, 4.4),
    ('FAIR',      'Fair (2.5–3.4)',      2.5, 3.4),
    ('POOR',      'Poor (0.0–2.4)',      0.0, 2.4)
ON DUPLICATE KEY UPDATE tier_label = VALUES(tier_label);
