#!/usr/bin/env python3
"""
Stdlib-only ETL runner (no pandas required).
Produces landing, silver, gold CSV layers for Power BI import.
Usage: python scripts/run_etl_stdlib.py
"""

from __future__ import annotations

import csv
import json
import re
import uuid
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "data/raw/vehicle_search/edge_pipeline_vehicle_search_2026-06-09.csv"
DATA = PROJECT / "data"

RENAME = {
    "Picture Count": "picture_count",
    "Stock Number": "stock_number",
    "Year": "model_year",
    "Make": "make",
    "Model": "model",
    "Style": "style",
    "Exterior Color": "exterior_color",
    "Mileage": "mileage",
    "Has Condition Report": "has_condition_report",
    "Grade": "grade",
    "Lights": "lights_raw",
    "Announcements": "announcements",
    "Vin": "vin",
}


def valid_vin(v: str) -> bool:
    v = v.strip().upper()
    return len(v) == 17 and bool(re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", v))


def mileage_bucket(m: int) -> str:
    if m in (0, 1):
        return "ANOMALY"
    if m < 30000:
        return "LOW"
    if m <= 100000:
        return "MEDIUM"
    return "HIGH"


def grade_tier(g: str) -> str:
    if not g.strip():
        return ""
    val = float(g)
    if val >= 4.5:
        return "EXCELLENT"
    if val >= 3.5:
        return "GOOD"
    if val >= 2.5:
        return "FAIR"
    return "POOR"


def primary_light(raw: str) -> str:
    if not raw.strip():
        return "UNKNOWN"
    return raw.split(",")[0].strip().upper() or "UNKNOWN"


def flags(text: str) -> dict[str, int]:
    u = text.upper()
    return {
        "is_as_is": int("AS IS" in u or "AS-IS" in u),
        "is_inop": int("INOP" in u),
        "has_structural_damage": int("STRUCTURAL" in u),
        "is_salvage": int("SALVAGE" in u or "TOTAL LOSS" in u),
        "is_repo": int("REPO" in u),
        "is_green_light": int("GREEN LIGHT" in u or "GREENLIGHT" in u),
    }


def drivetrain(style: str) -> str:
    s = style.upper()
    if "XDRIVE" in s or "XI" in s:
        return "AWD"
    if "SDRIVE" in s:
        return "RWD"
    return "UNKNOWN"


def transform_row(row: dict, batch_id: str, source_file: str) -> dict | None:
    vin = row["vin"].strip().upper()
    if not valid_vin(vin):
        return None
    try:
        year = int(row["model_year"])
        mileage = int(row["mileage"])
        if year < 1990 or year > 2030 or mileage < 0:
            return None
    except ValueError:
        return None

    ann = row.get("announcements") or ""
    f = flags(ann)
    snap = date.today()
    out = {
        "picture_count": row.get("picture_count", "0"),
        "stock_number": row["stock_number"].strip(),
        "model_year": year,
        "make": row["make"].strip().upper(),
        "model": row["model"].strip(),
        "style": row.get("style", "").strip() or None,
        "exterior_color": row["exterior_color"].strip().upper(),
        "mileage": mileage,
        "has_condition_report": 1 if str(row["has_condition_report"]).lower() == "true" else 0,
        "grade": row["grade"].strip() or None,
        "lights_raw": row.get("lights_raw", "").strip() or None,
        "announcements": ann.strip() or None,
        "vin": vin,
        "batch_id": batch_id,
        "source_file": source_file,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "primary_light": primary_light(row.get("lights_raw", "")),
        "mileage_bucket": mileage_bucket(mileage),
        "grade_tier": grade_tier(row.get("grade", "")),
        "drivetrain_type": drivetrain(row.get("style", "")),
        "wmi_prefix": vin[:3],
        "snapshot_date": snap.isoformat(),
        "vehicle_age": snap.year - year,
        **f,
    }
    return out


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        w.writerows(rows)


def main() -> dict:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Source CSV not found: {SOURCE}")

    batch_id = uuid.uuid4().hex[:12]
    source_file = SOURCE.name

    with SOURCE.open(encoding="utf-8-sig", newline="") as f:
        raw = list(csv.DictReader(f))

    renamed = [{RENAME.get(k, k): v for k, v in r.items()} for r in raw]
    valid, quarantine = [], []
    seen: set[str] = set()

    for r in renamed:
        t = transform_row(r, batch_id, source_file)
        if t is None:
            quarantine.append(r)
        elif t["vin"] in seen:
            quarantine.append(r)
        else:
            seen.add(t["vin"])
            valid.append(t)

    landing = DATA / "landing/vehicle_search" / f"landing_{batch_id}.csv"
    silver = DATA / "silver/vehicle_search" / f"silver_{batch_id}.csv"
    gold = DATA / "gold/vehicle_search" / f"gold_{batch_id}.csv"
    gold_latest = DATA / "gold/vehicle_search" / "gold_latest.csv"
    pbi = PROJECT / "powerbi/data/fct_vehicle_inventory.csv"
    quarantine_path = DATA / "quarantine/vehicle_search" / f"quarantine_{batch_id}.csv"

    write_csv(landing, renamed)
    write_csv(silver, valid)
    write_csv(gold, valid)
    write_csv(gold_latest, valid)
    write_csv(pbi, valid)
    write_csv(quarantine_path, quarantine)

    summary = {
        "batch_id": batch_id,
        "rows_extracted": len(raw),
        "rows_valid": len(valid),
        "rows_quarantined": len(quarantine),
        "gold_file": str(gold),
        "powerbi_export": str(pbi),
    }
    summary_path = DATA / "gold/vehicle_search" / f"run_summary_{batch_id}.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    main()
