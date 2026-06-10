"""CSV extraction from raw data zone."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd

from etl.constants import COLUMN_RENAME, REQUIRED_COLUMNS


def find_latest_csv(source_dir: Path) -> Path:
    csv_files = sorted(source_dir.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {source_dir}")
    return csv_files[0]


def extract_csv(source_path: Path, batch_id: str | None = None) -> tuple[pd.DataFrame, dict]:
    """Read CSV, rename columns, attach ingest metadata."""
    if not source_path.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    df = pd.read_csv(source_path, encoding="utf-8-sig")
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = df.rename(columns=COLUMN_RENAME)
    metadata = {
        "batch_id": batch_id or uuid4().hex[:12],
        "source_file": source_path.name,
        "source_path": str(source_path),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "row_count": len(df),
    }

    df["batch_id"] = metadata["batch_id"]
    df["source_file"] = metadata["source_file"]
    df["ingested_at"] = metadata["ingested_at"]

    return df, metadata
