#!/usr/bin/env python3
"""Generate standalone HTML dashboard from fct_vehicle_inventory.csv."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SRC = PROJECT / "powerbi" / "data" / "fct_vehicle_inventory.csv"
OUT = PROJECT / "powerbi" / "dashboard" / "vin-analytics.html"


def load_rows() -> list[dict]:
    with SRC.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def num(v, default=0):
    try:
        return float(v) if v not in ("", None) else default
    except (TypeError, ValueError):
        return default


def build_payload(rows: list[dict]) -> dict:
    grades = [num(r["grade"]) for r in rows if r.get("grade")]
    mileages = [int(num(r["mileage"])) for r in rows if r.get("mileage")]
    lights = Counter(r.get("primary_light") or "UNKNOWN" for r in rows)
    by_model: dict[str, list] = defaultdict(list)
    by_year: dict[int, list] = defaultdict(list)
    buckets = Counter(r.get("mileage_bucket") or "UNKNOWN" for r in rows)

    for r in rows:
        by_model[r["model"]].append(r)
        by_year[int(num(r["model_year"]))].append(r)

    top_models = sorted(by_model.items(), key=lambda x: -len(x[1]))[:10]
    scatter = [
        {"x": int(num(r["mileage"])), "y": num(r["grade"]), "m": r["model"]}
        for r in rows
        if r.get("grade") and r.get("mileage")
    ][:400]

    risk = sorted(
        [
            {
                "vin": r["vin"],
                "model": r["model"],
                "grade": num(r["grade"]),
                "mileage": int(num(r["mileage"])),
                "flags": ", ".join(
                    f for f, ok in [
                        ("AS IS", r.get("is_as_is") == "1"),
                        ("Structural", r.get("has_structural_damage") == "1"),
                        ("Salvage", r.get("is_salvage") == "1"),
                    ] if ok
                ) or "—",
            }
            for r in rows
            if r.get("is_as_is") == "1" or r.get("has_structural_damage") == "1" or num(r.get("grade")) < 2.5
        ],
        key=lambda x: (x["grade"] if x["grade"] else 99, -x["mileage"]),
    )[:15]

    return {
        "kpi": {
            "total": len(rows),
            "models": len(by_model),
            "avg_mileage": round(sum(mileages) / len(mileages)) if mileages else 0,
            "avg_grade": round(sum(grades) / len(grades), 2) if grades else 0,
            "condition_pct": round(100 * sum(1 for r in rows if r.get("has_condition_report") == "1") / len(rows), 1),
            "as_is": sum(1 for r in rows if r.get("is_as_is") == "1"),
            "structural": sum(1 for r in rows if r.get("has_structural_damage") == "1"),
        },
        "lights": {"labels": list(lights.keys()), "values": list(lights.values())},
        "top_models": {
            "labels": [m for m, _ in top_models],
            "counts": [len(v) for _, v in top_models],
            "grades": [round(sum(num(x["grade"]) for x in v if x.get("grade")) / max(1, sum(1 for x in v if x.get("grade"))), 2) for _, v in top_models],
        },
        "by_year": {
            "labels": sorted(by_year.keys()),
            "avg_grade": [
                round(sum(num(x["grade"]) for x in by_year[y] if x.get("grade")) / max(1, sum(1 for x in by_year[y] if x.get("grade"))), 2)
                for y in sorted(by_year.keys())
            ],
            "avg_mileage": [
                round(sum(int(num(x["mileage"])) for x in by_year[y]) / len(by_year[y]))
                for y in sorted(by_year.keys())
            ],
        },
        "buckets": {"labels": list(buckets.keys()), "values": list(buckets.values())},
        "scatter": scatter,
        "risk": risk,
    }


HTML = r"""<!DOCTYPE html>
<html lang="ka">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>VIN Analytics Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <style>
    :root { --bg:#f4f6f9; --card:#fff; --text:#1a1a2e; --muted:#5c6370; --accent:#1f4788; --border:#dde2ea; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: "Segoe UI", system-ui, sans-serif; background: var(--bg); color: var(--text); padding: 24px; }
    h1 { font-size: 1.5rem; font-weight: 600; margin-bottom: 4px; }
    .sub { color: var(--muted); font-size: 0.85rem; margin-bottom: 24px; }
    .kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 20px; }
    .kpi { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 16px; }
    .kpi .lbl { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; }
    .kpi .val { font-size: 1.75rem; font-weight: 700; color: var(--accent); margin-top: 4px; }
    .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 16px; }
    .card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 16px; }
    .card h2 { font-size: 0.9rem; font-weight: 600; margin-bottom: 12px; }
    .span6 { grid-column: span 6; } .span4 { grid-column: span 4; } .span8 { grid-column: span 8; } .span12 { grid-column: span 12; }
    canvas { max-height: 280px; }
    table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
    th, td { text-align: left; padding: 8px; border-bottom: 1px solid var(--border); }
    th { color: var(--muted); font-weight: 600; }
    @media (max-width: 900px) { .span6, .span4, .span8 { grid-column: span 12; } }
  </style>
</head>
<body>
  <h1>VIN Intelligence &amp; Car Market Analytics</h1>
  <p class="sub">BMW Auction Inventory · 555 vehicles · Source: fct_vehicle_inventory.csv</p>

  <div class="kpis" id="kpis"></div>
  <div class="grid">
    <div class="card span4"><h2>Auction Light Distribution</h2><canvas id="lights"></canvas></div>
    <div class="card span8"><h2>Top 10 Models by Count</h2><canvas id="models"></canvas></div>
    <div class="card span6"><h2>Avg Grade by Model Year</h2><canvas id="yearGrade"></canvas></div>
    <div class="card span6"><h2>Mileage Bucket Distribution</h2><canvas id="buckets"></canvas></div>
    <div class="card span8"><h2>Grade vs Mileage (scatter)</h2><canvas id="scatter"></canvas></div>
    <div class="card span4"><h2>Avg Grade — Top Models</h2><canvas id="modelGrade"></canvas></div>
    <div class="card span12"><h2>Risk Vehicles (low grade / flags)</h2>
      <table><thead><tr><th>VIN</th><th>Model</th><th>Grade</th><th>Mileage</th><th>Flags</th></tr></thead><tbody id="risk"></tbody></table>
    </div>
  </div>

  <script>
    const D = __DATA__;
    const fmt = n => n.toLocaleString();
    document.getElementById('kpis').innerHTML = [
      ['Total Vehicles', fmt(D.kpi.total)],
      ['Models', D.kpi.models],
      ['Avg Mileage', fmt(D.kpi.avg_mileage)],
      ['Avg Grade', D.kpi.avg_grade],
      ['Condition Report %', D.kpi.condition_pct + '%'],
      ['AS IS', D.kpi.as_is],
      ['Structural', D.kpi.structural],
    ].map(([l,v]) => `<div class="kpi"><div class="lbl">${l}</div><div class="val">${v}</div></div>`).join('');

    const colors = ['#1f4788','#c41e3a','#2d8f4e','#e8a317','#6b7280','#7c3aed','#0891b2'];
    const doughnut = (id, labels, values) => new Chart(document.getElementById(id), {
      type: 'doughnut', data: { labels, datasets: [{ data: values, backgroundColor: colors }] },
      options: { plugins: { legend: { position: 'bottom' } } }
    });
    doughnut('lights', D.lights.labels, D.lights.values);
    doughnut('buckets', D.buckets.labels, D.buckets.values);

    new Chart(document.getElementById('models'), {
      type: 'bar',
      data: { labels: D.top_models.labels, datasets: [{ label: 'Vehicle count', data: D.top_models.counts, backgroundColor: '#1f4788' }] },
      options: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, title: { display: true, text: 'Count' } } } }
    });

    new Chart(document.getElementById('modelGrade'), {
      type: 'bar',
      data: { labels: D.top_models.labels, datasets: [{ label: 'Avg grade', data: D.top_models.grades, backgroundColor: '#2d8f4e' }] },
      options: { indexAxis: 'y', plugins: { legend: { display: false } }, scales: { x: { min: 0, max: 5, title: { display: true, text: 'Grade (0–5)' } } } }
    });

    new Chart(document.getElementById('yearGrade'), {
      type: 'line',
      data: { labels: D.by_year.labels, datasets: [{ label: 'Avg grade', data: D.by_year.avg_grade, borderColor: '#1f4788', tension: 0.2 }] },
      options: { scales: { y: { min: 0, max: 5, title: { display: true, text: 'Avg grade' } }, x: { title: { display: true, text: 'Model year' } } } }
    });

    new Chart(document.getElementById('scatter'), {
      type: 'scatter',
      data: { datasets: [{ label: 'Vehicles', data: D.scatter, backgroundColor: 'rgba(31,71,136,0.5)', pointRadius: 4 }] },
      options: { scales: { x: { title: { display: true, text: 'Mileage' } }, y: { min: 0, max: 5, title: { display: true, text: 'Grade' } } } }
    });

    document.getElementById('risk').innerHTML = D.risk.map(r =>
      `<tr><td>${r.vin}</td><td>${r.model}</td><td>${r.grade || '—'}</td><td>${fmt(r.mileage)}</td><td>${r.flags}</td></tr>`
    ).join('');
  </script>
</body>
</html>
"""


def main() -> None:
    rows = load_rows()
    payload = build_payload(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    html = HTML.replace("__DATA__", json.dumps(payload))
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
