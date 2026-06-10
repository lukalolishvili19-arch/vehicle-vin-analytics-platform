"""End-to-end ETL pipeline runner."""

from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path

import pandas as pd

from etl.config import PipelineConfig, load_config, medallion_path
from etl.extract.csv_extractor import extract_csv, find_latest_csv
from etl.load.loader import MySQLLoader
from etl.transform.medallion import to_bronze, to_gold, to_silver, write_layer
from etl.validate.rules import validate_dataframe

logger = logging.getLogger("etl.pipeline")


def _write_csv(df: pd.DataFrame, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def _write_quarantine(quarantine: pd.DataFrame, data_root: Path, batch_id: str) -> Path | None:
    if quarantine.empty:
        return None
    out = medallion_path(data_root, "quarantine") / f"quarantine_{batch_id}.csv"
    return _write_csv(quarantine, out)


def run_pipeline(
    source_path: Path | None = None,
    config: PipelineConfig | None = None,
) -> dict:
    """Execute Extract → Validate → Transform → Load pipeline."""
    cfg = config or load_config()
    logger.info("Starting ETL pipeline [env=%s]", cfg.app_env)

    csv_path = source_path or find_latest_csv(cfg.source_csv_dir)
    logger.info("Extracting from %s", csv_path)

    # EXTRACT
    raw_df, metadata = extract_csv(csv_path)
    landing_path = medallion_path(cfg.data_root, "landing")
    landing_file = _write_csv(raw_df, landing_path / f"landing_{metadata['batch_id']}.csv")
    logger.info("Landing written: %s (%d rows)", landing_file, len(raw_df))

    # VALIDATE
    valid_df, quarantine_df = validate_dataframe(raw_df)
    quarantine_file = _write_quarantine(quarantine_df, cfg.data_root, metadata["batch_id"])
    logger.info("Validation: valid=%d, quarantined=%d", len(valid_df), len(quarantine_df))
    if quarantine_file:
        logger.warning("Quarantine file: %s", quarantine_file)

    # TRANSFORM
    bronze = to_bronze(valid_df)
    silver = to_silver(bronze)
    gold = to_gold(silver, snapshot_date=date.today())

    batch_id = metadata["batch_id"]
    bronze_file = write_layer(bronze, medallion_path(cfg.data_root, "bronze") / f"bronze_{batch_id}.parquet")
    silver_file = write_layer(silver, medallion_path(cfg.data_root, "silver") / f"silver_{batch_id}.parquet")
    gold_file = write_layer(gold, medallion_path(cfg.data_root, "gold") / f"gold_{batch_id}.parquet")
    logger.info("Medallion layers written: bronze, silver, gold")

    result = {
        "batch_id": batch_id,
        "source_file": metadata["source_file"],
        "rows_extracted": len(raw_df),
        "rows_valid": len(valid_df),
        "rows_quarantined": len(quarantine_df),
        "rows_silver": len(silver),
        "landing_file": str(landing_file),
        "bronze_file": str(bronze_file),
        "silver_file": str(silver_file),
        "gold_file": str(gold_file),
        "quarantine_file": str(quarantine_file) if quarantine_file else None,
        "mysql_load": None,
    }

    # LOAD (optional MySQL)
    if cfg.load_to_mysql:
        logger.info("Loading to MySQL [%s/%s]", cfg.mysql.host, cfg.mysql.database)
        loader = MySQLLoader(cfg.mysql)
        load_stats = loader.load(silver, metadata)
        if not quarantine_df.empty:
            load_stats["quarantine_rows"] = loader.load_quarantine(quarantine_df, metadata)
        result["mysql_load"] = load_stats
        logger.info("MySQL load complete: %s", load_stats)
    else:
        logger.info("MySQL load skipped (set LOAD_TO_MYSQL=true to enable)")

    summary_path = medallion_path(cfg.data_root, "gold") / f"run_summary_{batch_id}.json"
    summary_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    logger.info("Pipeline finished successfully")
    return result
