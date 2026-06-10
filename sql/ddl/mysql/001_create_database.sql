-- =============================================================================
-- 001_create_database.sql
-- MySQL database and user setup for vehicle analytics warehouse
-- =============================================================================

CREATE DATABASE IF NOT EXISTS vehicle_analytics
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE vehicle_analytics;

-- Optional application user (adjust password in production)
-- CREATE USER IF NOT EXISTS 'vehicle_user'@'%' IDENTIFIED BY 'changeme';
-- GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, INDEX, ALTER
--   ON vehicle_analytics.* TO 'vehicle_user'@'%';
-- FLUSH PRIVILEGES;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
