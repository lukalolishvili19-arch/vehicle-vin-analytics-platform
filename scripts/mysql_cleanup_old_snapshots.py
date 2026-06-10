#!/usr/bin/env python3
"""Keep only the latest inventory snapshot (removes duplicate snapshot rows)."""

from __future__ import annotations

import json

import pymysql

CFG = dict(host="localhost", port=3306, user="vehicle_user", password="changeme", database="vehicle_analytics", charset="utf8mb4")


def main() -> None:
    conn = pymysql.connect(**CFG)
    cur = conn.cursor()

    cur.execute("SELECT MAX(snapshot_key) FROM dim_inventory_snapshot")
    latest = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fct_vehicle_inventory WHERE snapshot_key <> %s", (latest,))
    to_delete = cur.fetchone()[0]

    cur.execute("DELETE FROM bridge_vehicle_lights WHERE inventory_key IN (SELECT inventory_key FROM fct_vehicle_inventory WHERE snapshot_key <> %s)", (latest,))
    cur.execute("DELETE FROM fct_vehicle_inventory WHERE snapshot_key <> %s", (latest,))
    cur.execute("DELETE FROM dim_inventory_snapshot WHERE snapshot_key <> %s", (latest,))

    cur.execute("SELECT COUNT(*) FROM fct_vehicle_inventory")
    remaining = cur.fetchone()[0]

    conn.commit()
    conn.close()

    print(json.dumps({"deleted_rows": to_delete, "remaining_rows": remaining, "latest_snapshot_key": latest}, indent=2))


if __name__ == "__main__":
    main()
