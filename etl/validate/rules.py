"""Row-level validation and quarantine split."""

from __future__ import annotations

import json

import pandas as pd

from etl.constants import MAX_GRADE, MAX_YEAR, MIN_GRADE, MIN_YEAR, REJECTION_CODES
from etl.validate.vin import is_valid_vin


def _row_errors(row: pd.Series, seen_vins: set[str]) -> list[dict]:
    errors: list[dict] = []

    vin = str(row.get("vin", "")).strip().upper()
    valid_vin, vin_msg = is_valid_vin(vin)
    if not valid_vin:
        errors.append({"code": REJECTION_CODES["INVALID_VIN"], "message": vin_msg})
    elif vin in seen_vins:
        errors.append({"code": REJECTION_CODES["DUPLICATE_VIN"], "message": f"Duplicate VIN: {vin}"})
    else:
        seen_vins.add(vin)

    try:
        year = int(row["model_year"])
        if year < MIN_YEAR or year > MAX_YEAR:
            errors.append(
                {
                    "code": REJECTION_CODES["INVALID_YEAR"],
                    "message": f"Year {year} outside {MIN_YEAR}-{MAX_YEAR}",
                }
            )
    except (TypeError, ValueError):
        errors.append({"code": REJECTION_CODES["INVALID_YEAR"], "message": "Invalid year value"})

    try:
        mileage = int(row["mileage"])
        if mileage < 0:
            errors.append(
                {"code": REJECTION_CODES["INVALID_MILEAGE"], "message": "Mileage cannot be negative"}
            )
    except (TypeError, ValueError):
        errors.append({"code": REJECTION_CODES["INVALID_MILEAGE"], "message": "Invalid mileage value"})

    grade_raw = row.get("grade")
    if pd.notna(grade_raw) and str(grade_raw).strip():
        try:
            grade = float(grade_raw)
            if grade < MIN_GRADE or grade > MAX_GRADE:
                errors.append(
                    {
                        "code": REJECTION_CODES["INVALID_GRADE"],
                        "message": f"Grade {grade} outside {MIN_GRADE}-{MAX_GRADE}",
                    }
                )
        except (TypeError, ValueError):
            errors.append({"code": REJECTION_CODES["INVALID_GRADE"], "message": "Invalid grade value"})

    return errors


def validate_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split dataframe into valid rows and quarantine rows."""
    seen_vins: set[str] = set()
    valid_indices: list[int] = []
    quarantine_rows: list[dict] = []

    for idx, row in df.iterrows():
        errors = _row_errors(row, seen_vins)
        if errors:
            q_row = row.to_dict()
            q_row["rejection_code"] = errors[0]["code"]
            q_row["rejection_reason"] = "; ".join(e["message"] for e in errors)
            q_row["validation_errors"] = json.dumps(errors)
            quarantine_rows.append(q_row)
        else:
            valid_indices.append(idx)

    valid_df = df.loc[valid_indices].copy().reset_index(drop=True)
    quarantine_df = pd.DataFrame(quarantine_rows)
    return valid_df, quarantine_df
