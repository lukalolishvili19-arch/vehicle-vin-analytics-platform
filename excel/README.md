# Phase 5 — Excel Analysis Guide

## Automated Workbook

**რეკომენდებული (pandas არ სჭირდება):**

```powershell
C:\msys64\ucrt64\bin\python.exe excel\generate_workbook_stdlib.py
```

ან ორმაგი კლიკი: `scripts\open_excel.bat`

Output: `excel/output/vehicle_analytics.xlsx`

**სრული ETL pipeline (pandas საჭიროა):**

```bash
pip install openpyxl pandas
python excel/generate_workbook.py
```

## Sheets Generated

| Sheet | Content | Excel Feature Equivalent |
|-------|---------|------------------------|
| **KPI Dashboard** | Total vehicles, avg mileage, avg grade, AS IS count | KPI cards |
| **By Model** | Pivot: model × count, avg mileage, avg grade | Pivot table |
| **By Year** | Model year trends | Pivot table + chart source |
| **By Color** | Color distribution | Pivot + bar chart |
| **By Light** | Auction light distribution | Slicer source |
| **Mileage Bucket** | LOW/MEDIUM/HIGH/ANOMALY | Conditional segments |
| **Detail Data** | Row-level records | Drill-through |

## Manual Enhancements in Excel

After opening the workbook:

1. **Pivot Tables** — Insert → PivotTable from `Detail Data` sheet
2. **Slicers** — Insert slicers on `model`, `model_year`, `primary_light`
3. **Charts**
   - Bar: Model vs vehicle count
   - Line: Year vs avg grade
   - Scatter: Mileage vs Grade
4. **Conditional Formatting**
   - Grade column: Red < 2.5, Yellow 2.5–3.5, Green > 3.5
   - Mileage: highlight > 100,000
5. **KPI Cards** — Link to KPI Dashboard sheet cells

## Note on Price

Price is **not in the dataset**. Use **Grade** as the quality/pricing proxy in charts and KPIs.
