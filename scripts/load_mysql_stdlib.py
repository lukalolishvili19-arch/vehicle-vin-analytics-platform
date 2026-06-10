#!/usr/bin/env python3
"""Load gold CSV into MySQL using pymysql (no pandas required)."""

from __future__ import annotations

import csv
import json
import uuid
from datetime import date
from pathlib import Path

import pymysql

PROJECT = Path(__file__).resolve().parents[1]
GOLD = PROJECT / "powerbi/data/fct_vehicle_inventory.csv"
if not GOLD.exists():
    candidates = sorted((PROJECT / "data/gold/vehicle_search").glob("gold_*.csv"), reverse=True)
    GOLD = candidates[0] if candidates else GOLD

CFG = dict(host="localhost", port=3306, user="vehicle_user", password="changeme", database="vehicle_analytics", charset="utf8mb4")


def load() -> dict:
    with GOLD.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    batch_id = rows[0].get("batch_id", uuid.uuid4().hex[:12]) if rows else uuid.uuid4().hex[:12]
    source_file = rows[0].get("source_file", GOLD.name) if rows else GOLD.name
    snapshot_date = date.today()

    conn = pymysql.connect(**CFG)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    cur.execute(
        "INSERT INTO audit_pipeline_run (pipeline_name, batch_id, source_file, status) VALUES (%s,%s,%s,'RUNNING')",
        ("vehicle_etl_stdlib", batch_id, source_file),
    )
    run_id = cur.lastrowid

    cur.execute(
        """INSERT INTO dim_inventory_snapshot (snapshot_date, source_file, batch_id, total_records, valid_records, quarantined_records)
           VALUES (%s,%s,%s,%s,%s,0)
           ON DUPLICATE KEY UPDATE total_records=VALUES(total_records), valid_records=VALUES(valid_records)""",
        (snapshot_date, source_file, batch_id, len(rows), len(rows)),
    )
    cur.execute("SELECT snapshot_key FROM dim_inventory_snapshot WHERE snapshot_date=%s AND source_file=%s", (snapshot_date, source_file))
    snapshot_key = cur.fetchone()["snapshot_key"]

    # Replace rows for this snapshot on re-load (idempotent)
    cur.execute(
        "DELETE FROM bridge_vehicle_lights WHERE inventory_key IN (SELECT inventory_key FROM fct_vehicle_inventory WHERE snapshot_key=%s)",
        (snapshot_key,),
    )
    cur.execute("DELETE FROM fct_vehicle_inventory WHERE snapshot_key=%s", (snapshot_key,))

    cur.execute("SELECT light_key, light_code FROM dim_auction_light")
    light_map = {r["light_code"]: r["light_key"] for r in cur.fetchall()}

    make_model_map: dict[tuple, int] = {}
    color_map: dict[str, int] = {}
    vehicle_map: dict[str, int] = {}

    def get_color(name: str) -> int:
        n = name or "UNKNOWN"
        if n not in color_map:
            cur.execute("INSERT IGNORE INTO dim_exterior_color (color_name, color_name_normalized) VALUES (%s,%s)", (n, n))
            cur.execute("SELECT color_key FROM dim_exterior_color WHERE color_name_normalized=%s", (n,))
            color_map[n] = cur.fetchone()["color_key"]
        return color_map[n]

    def get_make_model(make: str, model: str) -> int:
        key = (make, model)
        if key not in make_model_map:
            cur.execute(
                "INSERT INTO dim_make_model (make, model) VALUES (%s,%s) ON DUPLICATE KEY UPDATE make=make",
                (make, model),
            )
            cur.execute("SELECT make_model_key FROM dim_make_model WHERE make=%s AND model=%s", (make, model))
            make_model_map[key] = cur.fetchone()["make_model_key"]
        return make_model_map[key]

    fact_count = 0
    for r in rows:
        make, model = r["make"], r["model"]
        mm_key = get_make_model(make, model)
        color_key = get_color(r.get("exterior_color", "UNKNOWN"))
        vin = r["vin"]

        cur.execute("SELECT vehicle_key FROM dim_vehicle WHERE vin=%s AND is_current=1 LIMIT 1", (vin,))
        ex = cur.fetchone()
        if ex:
            vehicle_key = ex["vehicle_key"]
        else:
            cur.execute(
                """INSERT INTO dim_vehicle (vin, stock_number, make_model_key, color_key, model_year, style, wmi_prefix, effective_from, is_current)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,1)""",
                (vin, r["stock_number"], mm_key, color_key, int(r["model_year"]), r.get("style") or None, vin[:3], snapshot_date),
            )
            vehicle_key = cur.lastrowid
        vehicle_map[vin] = vehicle_key

        primary = (r.get("primary_light") or "UNKNOWN").upper()
        pl_key = light_map.get(primary, light_map.get("UNKNOWN", 6))
        grade = float(r["grade"]) if r.get("grade") and str(r["grade"]).strip() else None

        cur.execute(
            """INSERT INTO fct_vehicle_inventory (
                snapshot_key, vehicle_key, make_model_key, color_key, primary_light_key,
                vin, stock_number, model_year, make, model, style, exterior_color,
                picture_count, mileage, mileage_bucket, is_mileage_anomaly, vehicle_age,
                has_condition_report, grade, grade_tier, announcements,
                is_as_is, is_inop, has_structural_damage, is_salvage, is_repo, is_green_light,
                lights_raw, has_multiple_lights
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE mileage=VALUES(mileage), grade=VALUES(grade)""",
            (
                snapshot_key, vehicle_key, mm_key, color_key, pl_key,
                vin, r["stock_number"], int(r["model_year"]), make, model, r.get("style") or None, r["exterior_color"],
                int(r.get("picture_count") or 0), int(r["mileage"]), r.get("mileage_bucket", "MEDIUM"),
                1 if r.get("mileage_bucket") == "ANOMALY" else 0, int(r.get("vehicle_age") or 0),
                int(r.get("has_condition_report") or 0), grade, r.get("grade_tier") or None, r.get("announcements") or None,
                int(r.get("is_as_is") or 0), int(r.get("is_inop") or 0), int(r.get("has_structural_damage") or 0),
                int(r.get("is_salvage") or 0), int(r.get("is_repo") or 0), int(r.get("is_green_light") or 0),
                r.get("lights_raw") or None, 0,
            ),
        )
        inv_key = cur.lastrowid or None
        if not inv_key:
            cur.execute("SELECT inventory_key FROM fct_vehicle_inventory WHERE vin=%s AND snapshot_key=%s", (vin, snapshot_key))
            inv_key = cur.fetchone()["inventory_key"]
        cur.execute(
            "INSERT IGNORE INTO bridge_vehicle_lights (inventory_key, light_key, light_sequence, is_primary) VALUES (%s,%s,1,1)",
            (inv_key, pl_key),
        )
        fact_count += 1

    cur.execute(
        "UPDATE audit_pipeline_run SET status='SUCCESS', finished_at=UTC_TIMESTAMP(), rows_extracted=%s, rows_validated=%s, rows_loaded=%s WHERE run_id=%s",
        (len(rows), len(rows), fact_count, run_id),
    )
    conn.commit()
    conn.close()

    result = {"rows_loaded": fact_count, "snapshot_key": snapshot_key, "run_id": run_id}
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    load()
