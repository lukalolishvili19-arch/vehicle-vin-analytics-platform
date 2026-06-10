#!/usr/bin/env python3
"""Export MySQL tables to powerbi/data/ for Power BI Import mode."""

from __future__ import annotations

import csv
from pathlib import Path

import pymysql

PROJECT = Path(__file__).resolve().parents[1]
OUT = PROJECT / "powerbi" / "data"
CFG = dict(host="localhost", port=3306, user="vehicle_user", password="changeme", database="vehicle_analytics", charset="utf8mb4")

EXPORTS = {
    "fct_vehicle_inventory.csv": """
        SELECT f.*, al.light_name AS primary_light_name
        FROM fct_vehicle_inventory f
        JOIN dim_auction_light al ON f.primary_light_key = al.light_key
    """,
    "dim_make_model.csv": "SELECT * FROM dim_make_model",
    "dim_auction_light.csv": "SELECT * FROM dim_auction_light",
    "dim_exterior_color.csv": "SELECT * FROM dim_exterior_color",
    "vw_executive_kpi.csv": """
        SELECT
            COUNT(*) AS total_vehicles,
            COUNT(DISTINCT model) AS total_models,
            ROUND(AVG(mileage), 0) AS avg_mileage,
            ROUND(AVG(grade), 2) AS avg_grade,
            SUM(has_condition_report) AS with_condition_report,
            ROUND(100.0 * SUM(has_condition_report) / COUNT(*), 1) AS condition_report_pct,
            SUM(is_as_is) AS as_is_count,
            SUM(has_structural_damage) AS structural_count
        FROM fct_vehicle_inventory
    """,
    "agg_by_model.csv": """
        SELECT model, COUNT(*) AS vehicle_count,
               ROUND(AVG(mileage), 0) AS avg_mileage,
               ROUND(AVG(grade), 2) AS avg_grade,
               SUM(has_condition_report) AS with_report
        FROM fct_vehicle_inventory
        GROUP BY model ORDER BY vehicle_count DESC
    """,
}


def export_table(cur, sql: str, path: Path) -> int:
    cur.execute(sql)
    rows = cur.fetchall()
    if not rows:
        path.write_text("", encoding="utf-8")
        return 0
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    conn = pymysql.connect(**CFG)
    cur = conn.cursor(pymysql.cursors.DictCursor)
    for filename, sql in EXPORTS.items():
        n = export_table(cur, sql, OUT / filename)
        print(f"  {filename}: {n} rows")
    conn.close()
    print(f"\nExported to: {OUT}")


if __name__ == "__main__":
    main()
