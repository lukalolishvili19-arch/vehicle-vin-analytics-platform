"""Load transformed data into MySQL warehouse."""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, timezone

import pandas as pd

from etl.config import MySQLConfig
from etl.load.mysql_client import dict_cursor, mysql_connection

logger = logging.getLogger("etl.load")


class MySQLLoader:
    def __init__(self, cfg: MySQLConfig):
        self.cfg = cfg

    def load(self, silver: pd.DataFrame, metadata: dict) -> dict:
        snapshot_date = date.today()
        stats = {
            "staging_rows": 0,
            "quarantine_rows": 0,
            "fact_rows": 0,
            "snapshot_key": None,
            "run_id": None,
        }

        with mysql_connection(self.cfg) as conn:
            cursor = dict_cursor(conn)

            run_id = self._start_audit_run(cursor, metadata)
            stats["run_id"] = run_id

            snapshot_key = self._ensure_snapshot(cursor, metadata, snapshot_date, len(silver))
            stats["snapshot_key"] = snapshot_key

            make_model_map = self._upsert_make_models(cursor, silver)
            color_map = self._resolve_colors(cursor, silver)
            light_map = self._get_light_map(cursor)
            vehicle_map = self._upsert_vehicles(cursor, silver, make_model_map, color_map, snapshot_date)

            stats["staging_rows"] = self._load_staging(cursor, silver, metadata)
            stats["fact_rows"] = self._load_facts(
                cursor, silver, metadata, snapshot_key, make_model_map, color_map, light_map, vehicle_map, snapshot_date
            )

            self._finish_audit_run(cursor, run_id, "SUCCESS", stats)
            conn.commit()

        return stats

    def _start_audit_run(self, cursor, metadata: dict) -> int:
        cursor.execute(
            """
            INSERT INTO audit_pipeline_run
                (pipeline_name, batch_id, source_file, status, started_at)
            VALUES (%s, %s, %s, 'RUNNING', UTC_TIMESTAMP())
            """,
            ("vehicle_etl", metadata["batch_id"], metadata["source_file"]),
        )
        return cursor.lastrowid

    def _finish_audit_run(self, cursor, run_id: int, status: str, stats: dict) -> None:
        cursor.execute(
            """
            UPDATE audit_pipeline_run
            SET status = %s,
                finished_at = UTC_TIMESTAMP(),
                rows_extracted = %s,
                rows_validated = %s,
                rows_loaded = %s
            WHERE run_id = %s
            """,
            (status, stats.get("staging_rows", 0), stats.get("staging_rows", 0), stats.get("fact_rows", 0), run_id),
        )

    def _ensure_snapshot(self, cursor, metadata: dict, snapshot_date: date, row_count: int) -> int:
        cursor.execute(
            """
            INSERT INTO dim_inventory_snapshot
                (snapshot_date, source_file, batch_id, total_records, valid_records, quarantined_records)
            VALUES (%s, %s, %s, %s, %s, 0)
            ON DUPLICATE KEY UPDATE
                total_records = VALUES(total_records),
                valid_records = VALUES(valid_records),
                loaded_at = UTC_TIMESTAMP()
            """,
            (snapshot_date, metadata["source_file"], metadata["batch_id"], row_count, row_count),
        )
        cursor.execute(
            """
            SELECT snapshot_key FROM dim_inventory_snapshot
            WHERE snapshot_date = %s AND source_file = %s
            """,
            (snapshot_date, metadata["source_file"]),
        )
        row = cursor.fetchone()
        return row["snapshot_key"]

    def _upsert_make_models(self, cursor, df: pd.DataFrame) -> dict[tuple[str, str], int]:
        mapping: dict[tuple[str, str], int] = {}
        unique = df[["make", "model", "model_series", "is_electric", "is_m_series"]].drop_duplicates()

        for row in unique.itertuples(index=False):
            cursor.execute(
                """
                INSERT INTO dim_make_model (make, model, model_series, is_electric, is_m_series)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    model_series = VALUES(model_series),
                    is_electric = VALUES(is_electric),
                    is_m_series = VALUES(is_m_series)
                """,
                (row.make, row.model, row.model_series, int(row.is_electric), int(row.is_m_series)),
            )
            cursor.execute(
                "SELECT make_model_key FROM dim_make_model WHERE make = %s AND model = %s",
                (row.make, row.model),
            )
            mapping[(row.make, row.model)] = cursor.fetchone()["make_model_key"]

        return mapping

    def _resolve_colors(self, cursor, df: pd.DataFrame) -> dict[str, int]:
        mapping: dict[str, int] = {}
        for color in df["exterior_color_normalized"].dropna().unique():
            cursor.execute(
                """
                INSERT IGNORE INTO dim_exterior_color (color_name, color_name_normalized)
                VALUES (%s, %s)
                """,
                (color, color),
            )
            cursor.execute(
                "SELECT color_key FROM dim_exterior_color WHERE color_name_normalized = %s",
                (color,),
            )
            mapping[color] = cursor.fetchone()["color_key"]
        return mapping

    def _get_light_map(self, cursor) -> dict[str, int]:
        cursor.execute("SELECT light_key, light_code FROM dim_auction_light")
        return {row["light_code"]: row["light_key"] for row in cursor.fetchall()}

    def _upsert_vehicles(
        self,
        cursor,
        df: pd.DataFrame,
        make_model_map: dict,
        color_map: dict,
        snapshot_date: date,
    ) -> dict[str, int]:
        mapping: dict[str, int] = {}

        for row in df.itertuples(index=False):
            make_model_key = make_model_map[(row.make, row.model)]
            color_key = color_map[row.exterior_color_normalized]

            cursor.execute(
                """
                SELECT vehicle_key FROM dim_vehicle
                WHERE vin = %s AND is_current = 1
                LIMIT 1
                """,
                (row.vin,),
            )
            existing = cursor.fetchone()

            if existing:
                mapping[row.vin] = existing["vehicle_key"]
                continue

            cursor.execute(
                """
                INSERT INTO dim_vehicle
                    (vin, stock_number, make_model_key, color_key, model_year, style,
                     wmi_prefix, effective_from, is_current)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)
                """,
                (
                    row.vin,
                    row.stock_number,
                    make_model_key,
                    color_key,
                    int(row.model_year),
                    row.style if row.style not in (None, "None") else None,
                    row.wmi_prefix,
                    snapshot_date,
                ),
            )
            mapping[row.vin] = cursor.lastrowid

        return mapping

    def _load_staging(self, cursor, df: pd.DataFrame, metadata: dict) -> int:
        insert_sql = """
            INSERT INTO stg_vehicle_search (
                picture_count, stock_number, model_year, make, model, style,
                exterior_color, mileage, has_condition_report, grade,
                lights_raw, announcements, vin,
                source_file, batch_id, is_valid
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, 1
            )
        """
        rows = [
            (
                int(r.picture_count),
                r.stock_number,
                int(r.model_year),
                r.make,
                r.model,
                r.style if r.style not in (None, "None") else None,
                r.exterior_color,
                int(r.mileage),
                int(r.has_condition_report),
                None if pd.isna(r.grade) else float(r.grade),
                r.lights_raw if r.lights_raw not in (None, "None") else None,
                r.announcements if r.announcements not in (None, "None") else None,
                r.vin,
                metadata["source_file"],
                metadata["batch_id"],
            )
            for r in df.itertuples(index=False)
        ]
        cursor.executemany(insert_sql, rows)
        return len(rows)

    def _load_facts(
        self,
        cursor,
        df: pd.DataFrame,
        metadata: dict,
        snapshot_key: int,
        make_model_map: dict,
        color_map: dict,
        light_map: dict,
        vehicle_map: dict,
        snapshot_date: date,
    ) -> int:
        insert_sql = """
            INSERT INTO fct_vehicle_inventory (
                snapshot_key, vehicle_key, make_model_key, color_key, primary_light_key,
                vin, stock_number, model_year, make, model, style, exterior_color,
                picture_count, mileage, mileage_bucket, is_mileage_anomaly, vehicle_age,
                has_condition_report, grade, grade_tier,
                announcements, is_as_is, is_inop, has_structural_damage,
                is_salvage, is_repo, is_green_light,
                lights_raw, has_multiple_lights
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s
            )
            ON DUPLICATE KEY UPDATE
                mileage = VALUES(mileage),
                grade = VALUES(grade),
                loaded_at = UTC_TIMESTAMP()
        """

        bridge_sql = """
            INSERT IGNORE INTO bridge_vehicle_lights
                (inventory_key, light_key, light_sequence, is_primary)
            VALUES (%s, %s, %s, %s)
        """

        count = 0
        for row in df.itertuples(index=False):
            primary_light_key = light_map.get(row.primary_light, light_map.get("UNKNOWN", 6))
            vehicle_age = snapshot_date.year - int(row.model_year)

            cursor.execute(
                insert_sql,
                (
                    snapshot_key,
                    vehicle_map[row.vin],
                    make_model_map[(row.make, row.model)],
                    color_map[row.exterior_color_normalized],
                    primary_light_key,
                    row.vin,
                    row.stock_number,
                    int(row.model_year),
                    row.make,
                    row.model,
                    row.style if row.style not in (None, "None") else None,
                    row.exterior_color,
                    int(row.picture_count),
                    int(row.mileage),
                    row.mileage_bucket,
                    int(row.is_mileage_anomaly),
                    vehicle_age,
                    int(row.has_condition_report),
                    None if pd.isna(row.grade) else float(row.grade),
                    row.grade_tier,
                    row.announcements if row.announcements not in (None, "None") else None,
                    int(row.is_as_is),
                    int(row.is_inop),
                    int(row.has_structural_damage),
                    int(row.is_salvage),
                    int(row.is_repo),
                    int(row.is_green_light),
                    row.lights_raw if row.lights_raw not in (None, "None") else None,
                    int(row.has_multiple_lights),
                ),
            )

            inventory_key = cursor.lastrowid
            if not inventory_key:
                cursor.execute(
                    "SELECT inventory_key FROM fct_vehicle_inventory WHERE vin = %s AND snapshot_key = %s",
                    (row.vin, snapshot_key),
                )
                inventory_key = cursor.fetchone()["inventory_key"]

            lights = [row.primary_light]
            if row.secondary_lights:
                lights.extend(row.secondary_lights.split(","))
            for seq, light_code in enumerate(lights, start=1):
                light_key = light_map.get(light_code.strip(), light_map.get("UNKNOWN", 6))
                cursor.execute(bridge_sql, (inventory_key, light_key, seq, int(seq == 1)))

            count += 1

        return count

    def load_quarantine(self, quarantine: pd.DataFrame, metadata: dict) -> int:
        if quarantine.empty:
            return 0

        with mysql_connection(self.cfg) as conn:
            cursor = dict_cursor(conn)
            sql = """
                INSERT INTO stg_vehicle_search_quarantine (
                    picture_count, stock_number, model_year, make, model, style,
                    exterior_color, mileage, has_condition_report, grade,
                    lights_raw, announcements, vin,
                    rejection_reason, rejection_code, source_file, batch_id
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s
                )
            """
            rows = [
                (
                    r.get("picture_count"),
                    r.get("stock_number"),
                    r.get("model_year"),
                    r.get("make"),
                    r.get("model"),
                    r.get("style"),
                    r.get("exterior_color"),
                    r.get("mileage"),
                    r.get("has_condition_report"),
                    r.get("grade"),
                    r.get("lights_raw"),
                    r.get("announcements"),
                    r.get("vin"),
                    r.get("rejection_reason"),
                    r.get("rejection_code"),
                    metadata["source_file"],
                    metadata["batch_id"],
                )
                for r in quarantine.to_dict(orient="records")
            ]
            cursor.executemany(sql, rows)
            conn.commit()
            return len(rows)
