#!/usr/bin/env python3
"""Build Power BI helper CSVs from flat fct_vehicle_inventory.csv (no MySQL)."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SRC = PROJECT / "powerbi" / "data" / "fct_vehicle_inventory.csv"
OUT = PROJECT / "powerbi" / "data"


def read_rows() -> list[dict[str, str]]:
    with SRC.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    rows = read_rows()
    n = len(rows)

    # Executive KPI
    grades = [float(r["grade"]) for r in rows if r.get("grade")]
    mileages = [int(r["mileage"]) for r in rows if r.get("mileage")]
    models = {r["model"] for r in rows}
    with_report = sum(1 for r in rows if r.get("has_condition_report") == "1")
    write_csv(
        OUT / "vw_executive_kpi.csv",
        [
            "total_vehicles", "total_models", "avg_mileage", "avg_grade",
            "with_condition_report", "condition_report_pct", "as_is_count", "structural_count",
        ],
        [{
            "total_vehicles": n,
            "total_models": len(models),
            "avg_mileage": round(sum(mileages) / len(mileages)) if mileages else 0,
            "avg_grade": round(sum(grades) / len(grades), 2) if grades else 0,
            "with_condition_report": with_report,
            "condition_report_pct": round(100.0 * with_report / n, 1) if n else 0,
            "as_is_count": sum(1 for r in rows if r.get("is_as_is") == "1"),
            "structural_count": sum(1 for r in rows if r.get("has_structural_damage") == "1"),
        }],
    )

    # By model
    by_model: dict[str, list] = defaultdict(list)
    for r in rows:
        by_model[r["model"]].append(r)
    agg = []
    for model, mrows in sorted(by_model.items(), key=lambda x: -len(x[1])):
        g = [float(r["grade"]) for r in mrows if r.get("grade")]
        mi = [int(r["mileage"]) for r in mrows if r.get("mileage")]
        agg.append({
            "model": model,
            "vehicle_count": len(mrows),
            "avg_mileage": round(sum(mi) / len(mi)) if mi else 0,
            "avg_grade": round(sum(g) / len(g), 2) if g else 0,
            "with_report": sum(1 for r in mrows if r.get("has_condition_report") == "1"),
        })
    write_csv(OUT / "agg_by_model.csv", list(agg[0].keys()), agg)

    # Dim auction light
    lights: dict[str, int] = {}
    for r in rows:
        code = r.get("primary_light", "UNKNOWN")
        lights[code] = lights.get(code, 0) + 1
    light_rows = [{"light_code": k, "vehicle_count": v} for k, v in sorted(lights.items())]
    write_csv(OUT / "dim_auction_light_summary.csv", ["light_code", "vehicle_count"], light_rows)

    print(f"Source: {SRC} ({n} rows)")
    for name in ("vw_executive_kpi.csv", "agg_by_model.csv", "dim_auction_light_summary.csv"):
        print(f"  {name} OK")


if __name__ == "__main__":
    main()
