"""Medallion transformations: bronze → silver → gold."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import pandas as pd

from etl.constants import ANNOUNCEMENT_KEYWORDS, COLOR_NORMALIZATION, LIGHT_CODE_MAP
from etl.validate.anomalies import apply_anomaly_flags


def _normalize_color(value: str | None) -> str:
    if not value or not str(value).strip():
        return "UNKNOWN"
    normalized = str(value).strip().upper()
    return COLOR_NORMALIZATION.get(normalized, normalized)


def _parse_lights(value: str | None) -> tuple[str, list[str]]:
    if not value or not str(value).strip():
        return "UNKNOWN", []

    parts = [p.strip().upper() for p in str(value).split(",") if p.strip()]
    mapped = []
    for part in parts:
        code = LIGHT_CODE_MAP.get(part, part)
        if code not in mapped:
            mapped.append(code)

    if not mapped:
        return "UNKNOWN", []

    primary = mapped[0] if mapped[0] in LIGHT_CODE_MAP.values() else "UNKNOWN"
    secondary = mapped[1:] if len(mapped) > 1 else []
    return primary, secondary


def _mileage_bucket(mileage: int) -> tuple[str, bool]:
    if mileage in (0, 1):
        return "ANOMALY", True
    if mileage < 30000:
        return "LOW", False
    if mileage <= 100000:
        return "MEDIUM", False
    return "HIGH", False


def _grade_tier(grade: float | None) -> str | None:
    if grade is None or pd.isna(grade):
        return None
    if grade >= 4.5:
        return "EXCELLENT"
    if grade >= 3.5:
        return "GOOD"
    if grade >= 2.5:
        return "FAIR"
    return "POOR"


def _model_series(model: str) -> str | None:
    model = str(model).strip()
    if model.startswith("X") or model.startswith("Z"):
        return model[0]
    if model.startswith("i") or model.startswith("I"):
        return "i"
    if model.startswith("M") or " M" in model:
        return "M"
    match = re.match(r"^(\d+)", model.replace("-Series", ""))
    if match:
        return match.group(1)
    return None


def _announcement_flags(text: str | None) -> dict[str, bool]:
    upper = str(text or "").upper()
    flags = {}
    for flag_name, keywords in ANNOUNCEMENT_KEYWORDS.items():
        flags[flag_name] = any(kw in upper for kw in keywords)
    return flags


def _drivetrain_type(style: str | None) -> str:
    if not style or str(style).strip() in ("", "None", "nan"):
        return "UNKNOWN"
    upper = str(style).upper()
    if "XDRIVE" in upper or "XI " in upper or upper.endswith("XI"):
        return "AWD"
    if "SDRIVE" in upper:
        return "RWD"
    if "4WD" in upper or "4X4" in upper:
        return "4WD"
    return "UNKNOWN"


def to_bronze(df: pd.DataFrame) -> pd.DataFrame:
    """Validated raw data with minimal typing."""
    bronze = df.copy()
    bronze["vin"] = bronze["vin"].astype(str).str.strip().str.upper()
    bronze["stock_number"] = bronze["stock_number"].astype(str).str.strip()
    bronze["make"] = bronze["make"].astype(str).str.strip().str.upper()
    bronze["model"] = bronze["model"].astype(str).str.strip()
    bronze["style"] = bronze["style"].astype(str).replace({"nan": None, "": None})
    bronze["exterior_color"] = bronze["exterior_color"].astype(str).str.strip().str.upper()
    bronze["model_year"] = bronze["model_year"].astype(int)
    bronze["mileage"] = bronze["mileage"].astype(int)
    bronze["picture_count"] = bronze["picture_count"].fillna(0).astype(int)
    bronze["has_condition_report"] = (
        bronze["has_condition_report"].astype(str).str.lower().map({"true": 1, "false": 0}).fillna(0).astype(int)
    )
    bronze["grade"] = pd.to_numeric(bronze["grade"], errors="coerce")
    bronze["lights_raw"] = bronze["lights_raw"].astype(str).replace({"nan": None, "": None})
    bronze["announcements"] = bronze["announcements"].astype(str).replace({"nan": None, "": None})
    return bronze


def to_silver(bronze: pd.DataFrame) -> pd.DataFrame:
    """Clean, deduplicate, standardize."""
    silver = bronze.copy()
    silver["exterior_color_normalized"] = silver["exterior_color"].map(_normalize_color)
    silver["style"] = silver["style"].where(silver["style"].notna() & (silver["style"] != "None"), None)

    lights_parsed = silver["lights_raw"].map(_parse_lights)
    silver["primary_light"] = lights_parsed.map(lambda x: x[0])
    silver["secondary_lights"] = lights_parsed.map(lambda x: ",".join(x[1]) if x[1] else None)
    silver["has_multiple_lights"] = lights_parsed.map(lambda x: int(len(x[1]) > 0))

    mileage_info = silver["mileage"].map(_mileage_bucket)
    silver["mileage_bucket"] = mileage_info.map(lambda x: x[0])
    silver["is_mileage_anomaly"] = mileage_info.map(lambda x: int(x[1]))

    silver["grade_tier"] = silver["grade"].map(_grade_tier)
    silver["model_series"] = silver["model"].map(_model_series)
    silver["drivetrain_type"] = silver["style"].map(_drivetrain_type)
    silver["wmi_prefix"] = silver["vin"].str[:3]
    silver["is_electric"] = silver["model"].str.startswith("i").astype(int)
    silver["is_m_series"] = silver["model"].str.contains(r"\bM\d|M\d|-Series Grn|M Sports", regex=True).astype(int)

    flags = silver["announcements"].map(_announcement_flags).apply(pd.Series)
    silver = pd.concat([silver, flags], axis=1)

    silver = silver.sort_values(["vin", "ingested_at"]).drop_duplicates(subset=["vin"], keep="last")
    silver = apply_anomaly_flags(silver)
    return silver.reset_index(drop=True)


def to_gold(silver: pd.DataFrame, snapshot_date: date | None = None) -> pd.DataFrame:
    """Business-ready dataset with derived analytics fields."""
    gold = silver.copy()
    snap = snapshot_date or date.today()
    gold["snapshot_date"] = snap.isoformat()
    gold["vehicle_age"] = snap.year - gold["model_year"]
    return gold


def write_layer(df: pd.DataFrame, output_path: Path) -> Path:
    """Write dataframe to Parquet if available, otherwise CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        df.to_parquet(output_path, index=False)
    except (ImportError, ModuleNotFoundError):
        csv_path = output_path.with_suffix(".csv")
        df.to_csv(csv_path, index=False)
        return csv_path
    return output_path
