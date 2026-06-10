"""
Generate Excel analysis workbook from gold layer CSV or raw source.

Usage:
    python excel/generate_workbook.py
    python excel/generate_workbook.py --source data/raw/vehicle_search/edge_pipeline_vehicle_search_2026-06-09.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from etl.constants import COLUMN_RENAME
from etl.transform.medallion import to_bronze, to_gold, to_silver
from etl.validate.rules import validate_dataframe


def _find_gold_csv() -> Path | None:
    gold_dir = PROJECT_ROOT / "data" / "gold" / "vehicle_search"
    files = sorted(gold_dir.glob("gold_*.csv"), reverse=True)
    return files[0] if files else None


def load_data(source: Path | None) -> pd.DataFrame:
    if source and source.exists():
        df = pd.read_csv(source, encoding="utf-8-sig").rename(columns=COLUMN_RENAME)
        valid, _ = validate_dataframe(df)
        return to_gold(to_silver(to_bronze(valid)))
    gold = _find_gold_csv()
    if gold:
        return pd.read_csv(gold)
    raise FileNotFoundError("No gold CSV or source file found. Run ETL first.")


def generate_workbook(df: pd.DataFrame, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)

    # KPI sheet
    kpi = pd.DataFrame(
        [
            {"Metric": "Total Vehicles", "Value": len(df)},
            {"Metric": "Unique Models", "Value": df["model"].nunique()},
            {"Metric": "Avg Mileage", "Value": round(df["mileage"].mean(), 0)},
            {"Metric": "Avg Grade", "Value": round(df["grade"].mean(), 2) if df["grade"].notna().any() else None},
            {"Metric": "Condition Report %", "Value": round(100 * df["has_condition_report"].mean(), 1)},
            {"Metric": "AS IS Count", "Value": int(df.get("is_as_is", pd.Series([0])).sum())},
            {"Metric": "Green Light Count", "Value": int((df["primary_light"] == "GREEN").sum())},
            {"Metric": "Red Light Count", "Value": int((df["primary_light"] == "RED").sum())},
        ]
    )

    # Pivot-like summaries
    by_model = (
        df.groupby("model")
        .agg(vehicles=("vin", "count"), avg_mileage=("mileage", "mean"), avg_grade=("grade", "mean"))
        .round(2)
        .sort_values("vehicles", ascending=False)
        .reset_index()
    )

    by_year = (
        df.groupby("model_year")
        .agg(count=("vin", "count"), avg_grade=("grade", "mean"), avg_mileage=("mileage", "mean"))
        .round(2)
        .reset_index()
        .sort_values("model_year", ascending=False)
    )

    by_color = df.groupby("exterior_color_normalized").size().reset_index(name="count").sort_values("count", ascending=False)
    by_light = df.groupby("primary_light").size().reset_index(name="count").sort_values("count", ascending=False)
    by_mileage_bucket = df.groupby("mileage_bucket").size().reset_index(name="count")

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        kpi.to_excel(writer, sheet_name="KPI Dashboard", index=False)
        by_model.to_excel(writer, sheet_name="By Model", index=False)
        by_year.to_excel(writer, sheet_name="By Year", index=False)
        by_color.to_excel(writer, sheet_name="By Color", index=False)
        by_light.to_excel(writer, sheet_name="By Light", index=False)
        by_mileage_bucket.to_excel(writer, sheet_name="Mileage Bucket", index=False)
        df.head(500).to_excel(writer, sheet_name="Detail Data", index=False)

        # Format KPI sheet (conditional-style via openpyxl)
        ws = writer.sheets["KPI Dashboard"]
        ws.column_dimensions["A"].width = 28
        ws.column_dimensions["B"].width = 18

    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "excel" / "output" / "vehicle_analytics.xlsx")
    args = parser.parse_args()

    df = load_data(args.source)
    out = generate_workbook(df, args.output)
    print(f"Excel workbook created: {out}")


if __name__ == "__main__":
    main()
