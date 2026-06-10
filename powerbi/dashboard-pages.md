# Power BI Dashboard — Page Specifications

> **Note:** Use **Grade** instead of Price throughout. Picture Count replaces image URL.

---

## Page 1: Executive Overview

| Visual | Field | Type |
|--------|-------|------|
| Card | Total Vehicles | Measure |
| Card | Avg Mileage | Measure |
| Card | Avg Grade | Measure |
| Card | Total Models | Measure |
| Donut | primary_light / light_name | Dimension |
| Bar | model vs Total Vehicles | Top 10 |
| Line | model_year vs Avg Grade | Trend |

**Slicers:** model_year, mileage_bucket, has_condition_report

---

## Page 2: Brand / Model Analysis

| Visual | Field |
|--------|-------|
| Treemap | model × Total Vehicles |
| Bar | Model Share % |
| Table | model, Total Vehicles, Avg Grade, Avg Mileage |
| Clustered bar | model vs Avg Grade by Model |

**Slicers:** model, grade_tier

---

## Page 3: VIN Analysis

| Visual | Field |
|--------|-------|
| Search slicer | dim_vehicle[vin] |
| Table | vin, stock_number, model, style, grade, mileage, announcements |
| Map (optional) | wmi_prefix / build_region from ref_vin_wmi |
| Histogram | grade distribution |

**Drill-through:** VIN → vehicle detail table

---

## Page 4: Quality & Mileage Analysis

| Visual | Field |
|--------|-------|
| Scatter | mileage (X) vs grade (Y), size = picture_count |
| Column | mileage_bucket vs Avg Grade |
| Line | model_year vs Avg Mileage |
| KPI | Condition Report % |

*Replaces "Price vs Mileage" — not available in source.*

---

## Page 5: Insights & Risk

| Visual | Field |
|--------|-------|
| Card | AS IS Count, Structural Damage Count, High Risk Count |
| Bar | announcement flags (is_as_is, is_inop, is_salvage) |
| Table | bottom risk vehicles (grade < 2, flags) |
| Text box | Link to docs/insights/business-insights.md |

**KPI trend:** Green Light % vs Red Light %

---

## Screenshots

Place exported PNGs in:

```
docs/screenshots/
├── pbi_page1_executive.png
├── pbi_page2_model.png
├── pbi_page3_vin.png
├── pbi_page4_quality_mileage.png
└── pbi_page5_insights.png
```
