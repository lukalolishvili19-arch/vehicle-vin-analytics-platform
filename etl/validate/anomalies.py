"""Anomaly and outlier detection using numpy."""

from __future__ import annotations

import numpy as np
import pandas as pd


def detect_mileage_outliers(df: pd.DataFrame, column: str = "mileage") -> pd.Series:
    """IQR-based outlier flag for mileage."""
    values = df[column].astype(float)
    q1, q3 = np.percentile(values, [25, 75])
    iqr = q3 - q1
    lower = max(0, q1 - 1.5 * iqr)
    upper = q3 + 1.5 * iqr
    return (values < lower) | (values > upper)


def detect_grade_outliers(df: pd.DataFrame, column: str = "grade") -> pd.Series:
    """Flag grades outside 0–5 or statistical outliers when grade present."""
    grades = pd.to_numeric(df[column], errors="coerce")
    valid = grades.dropna()
    if valid.empty:
        return pd.Series(False, index=df.index)
    q1, q3 = np.percentile(valid, [25, 75])
    iqr = q3 - q1
    lower = max(0, q1 - 1.5 * iqr)
    upper = min(5, q3 + 1.5 * iqr)
    return grades.notna() & ((grades < lower) | (grades > upper))


def apply_anomaly_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Add anomaly columns to silver dataframe."""
    result = df.copy()
    result["is_mileage_iqr_outlier"] = detect_mileage_outliers(result).astype(int)
    result["is_grade_outlier"] = detect_grade_outliers(result).astype(int)
    result["is_picture_count_zero"] = (result["picture_count"] == 0).astype(int)
    return result
