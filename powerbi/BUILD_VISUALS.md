# Power BI — ვიზუალიზაციები ნაბიჯ-ნაბიჯ

> CSV უკვე ჩატვირთული გაქვს? თუ არა → `IMPORT_CSV.md`

## თემა (1 წუთი)

**View → Themes → Browse for themes** → აირჩიე `powerbi/theme/VIN-Analytics.json`

---

## Measures (Modeling → New measure)

კოპირება `dax-measures-flat.dax`-დან — მინიმუმ:

- `Total Vehicles`
- `Avg Mileage`
- `Avg Grade`
- `Total Models`
- `Condition Report %`
- `AS IS Count`

---

## გვერდი 1: Executive Overview

1. **Insert → Card** × 4 — ველები: ზემოთ measures
2. **Donut chart** — Legend: `primary_light`, Values: `Total Vehicles`
3. **Clustered bar** — Axis: `model`, Values: `Total Vehicles`
   - Filters on visual → Top N → 10
4. **Line chart** — Axis: `model_year`, Values: `Avg Grade`
5. **Slicers** (მარჯვნივ): `model_year`, `mileage_bucket`, `has_condition_report`

გვერდის სახელი: `Executive`

---

## გვერდი 2: Models

1. **Treemap** — Category: `model`, Values: `Total Vehicles`
2. **Table** — `model`, `Total Vehicles`, `Avg Grade`, `Avg Mileage`
3. **Clustered bar** — `model` (Top 8), `Avg Grade`

გვერდის სახელი: `Models`

---

## გვერდი 3: VIN

1. **Slicer** — `vin` → Format → Style: **Dropdown**, Search: On
2. **Table** — `vin`, `stock_number`, `model`, `style`, `grade`, `mileage`, `announcements`

გვერდის სახელი: `VIN Lookup`

---

## გვერდი 4: Quality

1. **Scatter** — X: `mileage`, Y: `grade`, Size: `picture_count`
2. **Column** — Axis: `mileage_bucket`, Values: `Total Vehicles`
3. **Line** — Axis: `model_year`, Values: `Avg Mileage`

გვერდის სახელი: `Quality`

---

## გვერდი 5: Risk

1. **Card** — `AS IS Count`, `Structural Damage Count`
2. **Bar** — `primary_light` = RED vs GREEN, `Total Vehicles`
3. **Table** — `vin`, `model`, `grade`, `is_as_is`, `announcements`
   - Filter: `grade` < 2.5 OR `is_as_is` = 1

გვერდის სახელი: `Risk`

---

## შენახვა

**File → Save as** → `powerbi/VIN_Analytics.pbix`

## ბრაუზერში preview (სწრაფი)

```powershell
python powerbi\generate_html_dashboard.py
start powerbi\dashboard\vin-analytics.html
```
