"""Configuration loader for ETL pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULTS = {
    "paths": {"data_root": "data", "source_csv": "data/raw/vehicle_search"},
    "pipeline": {"batch_size": 1000, "quarantine_on_error": True},
    "mysql": {
        "host": "localhost",
        "port": 3306,
        "database": "vehicle_analytics",
        "user": "vehicle_user",
        "password": "changeme",
    },
    "log_level": "INFO",
}


@dataclass
class MySQLConfig:
    host: str
    port: int
    database: str
    user: str
    password: str
    enabled: bool


@dataclass
class PipelineConfig:
    data_root: Path
    source_csv_dir: Path
    batch_size: int
    quarantine_on_error: bool
    load_to_mysql: bool
    app_env: str
    log_level: str
    mysql: MySQLConfig


def _load_yaml(env: str) -> dict:
    try:
        import yaml
    except ImportError:
        return {}

    config_path = PROJECT_ROOT / "config" / "environments" / f"{env}.yaml"
    if not config_path.exists():
        return {}
    with config_path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(env: str | None = None) -> PipelineConfig:
    load_dotenv(PROJECT_ROOT / ".env")
    app_env = env or os.getenv("APP_ENV", "dev")
    yaml_cfg = _merge(DEFAULTS, _load_yaml(app_env))

    paths = yaml_cfg.get("paths", {})
    pipeline = yaml_cfg.get("pipeline", {})
    mysql_yaml = yaml_cfg.get("mysql", {})

    data_root = PROJECT_ROOT / paths.get("data_root", "data")
    source_csv_dir = PROJECT_ROOT / paths.get("source_csv", "data/raw/vehicle_search")

    return PipelineConfig(
        data_root=data_root,
        source_csv_dir=source_csv_dir,
        batch_size=int(pipeline.get("batch_size", 1000)),
        quarantine_on_error=bool(pipeline.get("quarantine_on_error", True)),
        load_to_mysql=os.getenv("LOAD_TO_MYSQL", "false").lower() == "true",
        app_env=app_env,
        log_level=os.getenv("LOG_LEVEL", yaml_cfg.get("log_level", "INFO")),
        mysql=MySQLConfig(
            host=os.getenv("MYSQL_HOST", mysql_yaml.get("host", "localhost")),
            port=int(os.getenv("MYSQL_PORT", mysql_yaml.get("port", 3306))),
            database=os.getenv("MYSQL_DATABASE", mysql_yaml.get("database", "vehicle_analytics")),
            user=os.getenv("MYSQL_USER", mysql_yaml.get("user", "vehicle_user")),
            password=os.getenv("MYSQL_PASSWORD", mysql_yaml.get("password", "changeme")),
            enabled=os.getenv("LOAD_TO_MYSQL", "false").lower() == "true",
        ),
    )


def medallion_path(data_root: Path, layer: str, dataset: str = "vehicle_search") -> Path:
    return data_root / layer / dataset
