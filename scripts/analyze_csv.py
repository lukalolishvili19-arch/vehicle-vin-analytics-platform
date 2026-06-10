"""Temporary CSV profiling script."""
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "data/raw/vehicle_search/edge_pipeline_vehicle_search_2026-06-09.csv"

with path.open(encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

cols = rows[0].keys() if rows else []
print("=== BASIC ===")
print("file:", path.name)
print("rows:", len(rows))
print("columns:", len(cols))
print("column_names:", list(cols))

print("\n=== NULL / EMPTY COUNTS ===")
for c in cols:
    empty = sum(1 for r in rows if not str(r.get(c, "")).strip())
    pct = round(100 * empty / len(rows), 1)
    print(f"{c}: {empty} ({pct}%)")

years = [int(r["Year"]) for r in rows if str(r.get("Year", "")).strip().isdigit()]
mileages = [int(r["Mileage"]) for r in rows if str(r.get("Mileage", "")).strip().lstrip("-").isdigit()]
grades = [float(r["Grade"]) for r in rows if str(r.get("Grade", "")).strip()]

print("\n=== YEAR ===")
print("min:", min(years), "max:", max(years))
print("distribution:", dict(sorted(Counter(r["Year"] for r in rows).items())))

print("\n=== MAKE / MODEL ===")
print("makes:", Counter(r["Make"] for r in rows))
models = Counter(r["Model"] for r in rows)
print("unique_models:", len(models))
print("top_10_models:", models.most_common(10))

print("\n=== STYLE ===")
style_empty = sum(1 for r in rows if not str(r.get("Style", "")).strip())
print("empty_style:", style_empty)
print("unique_styles:", len(set(r["Style"] for r in rows if str(r.get("Style", "")).strip())))

print("\n=== EXTERIOR COLOR ===")
colors = Counter(r["Exterior Color"] for r in rows if str(r.get("Exterior Color", "")).strip())
print("unique_colors:", len(colors))
print("top_colors:", colors.most_common(8))

print("\n=== MILEAGE ===")
print("min:", min(mileages), "max:", max(mileages), "avg:", round(sum(mileages) / len(mileages), 1))
mileage_anomalies = [r for r in rows if str(r.get("Mileage", "")).strip() in ("0", "1")]
print("mileage_0_or_1:", len(mileage_anomalies))

print("\n=== HAS CONDITION REPORT ===")
print(Counter(r["Has Condition Report"] for r in rows))

print("\n=== GRADE ===")
print("filled:", len(grades), "empty:", len(rows) - len(grades))
if grades:
    print("min:", min(grades), "max:", max(grades), "avg:", round(sum(grades) / len(grades), 2))

print("\n=== LIGHTS ===")
lights = Counter(r["Lights"] for r in rows)
print("unique_lights_values:", len(lights))
print("lights_distribution:", lights.most_common(12))
multi_light = [r for r in rows if "," in str(r.get("Lights", ""))]
print("multi_value_lights:", len(multi_light))

print("\n=== ANNOUNCEMENTS ===")
ann_empty = sum(1 for r in rows if not str(r.get("Announcements", "")).strip())
print("empty:", ann_empty, "filled:", len(rows) - ann_empty)
keywords = ["AS IS", "STRUCTURAL", "GREEN LIGHT", "INOP", "SALVAGE", "REPO", "TOTAL LOSS"]
for kw in keywords:
    cnt = sum(1 for r in rows if kw.lower() in str(r.get("Announcements", "")).lower())
    if cnt:
        print(f'  keyword "{kw}": {cnt}')

print("\n=== VIN ===")
vins = [str(r.get("Vin", "")).strip() for r in rows]
print("total:", len(vins), "unique:", len(set(vins)))
bad_len = [v for v in vins if len(v) != 17]
print("bad_length:", len(bad_len))
dup_vins = [v for v, c in Counter(vins).items() if c > 1]
print("duplicate_vins:", len(dup_vins))
invalid_chars = [v for v in vins if re.search(r"[^A-HJ-NPR-Z0-9]", v.upper())]
print("invalid_vin_chars:", len(invalid_chars))

print("\n=== STOCK NUMBER ===")
stocks = [str(r.get("Stock Number", "")).strip() for r in rows]
print("unique_stock:", len(set(stocks)), "duplicates:", len(stocks) - len(set(stocks)))

print("\n=== PICTURE COUNT ===")
pics = [int(r["Picture Count"]) for r in rows if str(r.get("Picture Count", "")).strip().isdigit()]
print("min:", min(pics), "max:", max(pics), "avg:", round(sum(pics) / len(pics), 1))
zero_pics = sum(1 for p in pics if p == 0)
print("zero_picture_count:", zero_pics)

print("\n=== DATA QUALITY FLAGS ===")
flags = {
    "missing_style": sum(1 for r in rows if not str(r.get("Style", "")).strip()),
    "missing_grade": sum(1 for r in rows if not str(r.get("Grade", "")).strip()),
    "missing_lights": sum(1 for r in rows if not str(r.get("Lights", "")).strip()),
    "no_condition_report": sum(1 for r in rows if str(r.get("Has Condition Report", "")).lower() == "false"),
    "grade_without_report": sum(
        1
        for r in rows
        if str(r.get("Grade", "")).strip() and str(r.get("Has Condition Report", "")).lower() == "false"
    ),
    "report_without_grade": sum(
        1
        for r in rows
        if not str(r.get("Grade", "")).strip() and str(r.get("Has Condition Report", "")).lower() == "true"
    ),
}
for k, v in flags.items():
    print(f"{k}: {v}")

print("\n=== CROSS: MODEL x AVG GRADE (top 8 by count, min 5 graded) ===")
model_grades = defaultdict(list)
for r in rows:
    if str(r.get("Grade", "")).strip():
        model_grades[r["Model"]].append(float(r["Grade"]))
ranked = sorted(
    ((m, sum(g) / len(g), len(g)) for m, g in model_grades.items() if len(g) >= 5),
    key=lambda x: -x[2],
)[:8]
for m, avg, n in ranked:
    print(f"  {m}: avg_grade={avg:.2f} (n={n})")
