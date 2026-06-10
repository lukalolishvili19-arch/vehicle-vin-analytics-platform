# Phase 1 — Full Data Analysis Report

**Dataset:** `edge_pipeline_vehicle_search_2026-06-09.csv`  
**Domain:** BMW wholesale / auction vehicle inventory (Edge Pipeline Vehicle Search)  
**Records:** 555 vehicles | **Columns:** 13

---

## 1. Dataset Summary

| Metric | Value |
|--------|-------|
| Rows | 555 |
| Columns | 13 |
| Manufacturer | BMW only (100%) |
| Model years | 2013 – 2026 |
| Unique VINs | 555 (100% unique) |
| Unique stock numbers | 555 (100% unique) |
| Duplicate rows | 0 |

### Fields NOT present in source data

The following are **not available** and must not be assumed in analytics:

- Price / MSRP / sale price
- Fuel type
- Transmission type (explicit column)
- Geographic location / state / dealer region
- Image URL / image path (only `Picture Count` — number of listing photos)

Analytics use **Grade** (auction condition score), **Mileage**, **Lights**, and **Announcements** as market-quality proxies.

---

## 2. Column Profile

| Column | Type | Null/Empty | Business Meaning |
|--------|------|------------|------------------|
| **Picture Count** | Integer | 0% | Number of photos in listing; proxy for listing completeness |
| **Stock Number** | String | 0% | Auction house inventory ID |
| **Year** | Integer | 0% | Model year |
| **Make** | String | 0% | Manufacturer (always BMW in this extract) |
| **Model** | String | 0% | Model line (3-Series, X5, etc.) |
| **Style** | String | 4.0% empty | Trim / drivetrain variant (330i, xDrive, M40i) |
| **Exterior Color** | String | 0% | Exterior paint color |
| **Mileage** | Integer | 0% | Odometer reading (miles) |
| **Has Condition Report** | Boolean | 0% | Whether a formal condition report exists |
| **Grade** | Float (0–5) | 37.3% empty | Auction condition grade (higher = better) |
| **Lights** | String | 31.7% empty | Auction signal: Green / Red / Yellow / White / Blue |
| **Announcements** | Text | 58.4% empty | Seller notes (AS IS, structural damage, etc.) |
| **Vin** | String (17) | 0% | Vehicle Identification Number — **business key** |

---

## 3. Missing Values

| Column | Missing Count | Missing % | Handling Strategy |
|--------|---------------|-----------|-------------------|
| Style | 22 | 4.0% | Allow NULL |
| Grade | 207 | 37.3% | NULL (often when no condition report) |
| Lights | 176 | 31.7% | Default to `UNKNOWN` |
| Announcements | 324 | 58.4% | NULL + derived boolean flags |

**Cross-field pattern:** 29 vehicles have `Has Condition Report = true` but empty Grade.

---

## 4. Duplicates & Keys

| Key | Unique | Duplicates | Recommendation |
|-----|--------|------------|----------------|
| VIN | 555 | 0 | **Primary business key** |
| Stock Number | 555 | 0 | Alternate key |

---

## 5. Outliers & Anomalies

| Field | Anomaly | Count | Notes |
|-------|---------|-------|-------|
| Mileage | 0 or 1 miles | 5 | Likely placeholder / new listing |
| Mileage | > 200,000 | 8 | High-mileage fleet units |
| Mileage | Max 239,654 | 1 | Extreme outlier (X1 2017) |
| Grade | 0.0 | 4 | Poor condition / inoperable |
| Grade | 5.0 | 3 | Top grade |
| Picture Count | 0 | 11 | Listings without photos |
| Picture Count | Max 61 | 1 | Rich media listing |

---

## 6. Categorical Distributions

### Top Models
| Model | Count | Share |
|-------|-------|-------|
| 3-Series | 115 | 20.7% |
| X3 | 92 | 16.6% |
| X5 | 88 | 15.9% |
| 5-Series | 67 | 12.1% |
| X1 | 44 | 7.9% |

### Exterior Color
| Color | Count |
|-------|-------|
| BLACK | 194 |
| WHITE | 139 |
| GRAY | 84 |
| BLUE | 58 |

### Auction Lights
| Light | Count |
|-------|-------|
| Red | 238 |
| (empty) | 176 |
| Green | 117 |
| Multi-value | 10 |

### Condition Report
| Value | Count | % |
|-------|-------|---|
| true | 377 | 67.9% |
| false | 178 | 32.1% |

### Grade (when present)
- **Average:** 3.49 | **Min:** 0.0 | **Max:** 5.0

---

## 7. Derived Attributes (ETL)

| Derived Field | Source Logic |
|---------------|--------------|
| `drivetrain_type` | Parsed from Style: xDrive / sDrive / AWD / RWD |
| `mileage_bucket` | LOW / MEDIUM / HIGH / ANOMALY |
| `grade_tier` | EXCELLENT / GOOD / FAIR / POOR |
| `wmi_prefix` | First 3 VIN characters → region lookup |
| `vehicle_age` | Snapshot year − model year |
| `is_as_is`, `is_inop`, etc. | Keyword extraction from Announcements |
| `listing_image_count` | From Picture Count (no URL in source) |

---

## 8. Data Model Recommendations

1. **Star schema** with `fct_vehicle_inventory` at VIN × snapshot grain
2. **VIN as natural key** in `dim_vehicle` with SCD Type 2 for attribute changes
3. **Bridge table** for multi-value Lights
4. **Do not add** price/fuel/geo columns without new data sources
5. **Picture Count** stored as measure; optional future `image_url` column when API available
6. **Quarantine table** for invalid VIN/year/mileage rows
7. **Grade** nullable — do not impute with zero

---

## 9. Data Quality Score

| Dimension | Score | Notes |
|-----------|-------|-------|
| Completeness (core keys) | 100% | VIN, Year, Make, Model always present |
| Uniqueness | 100% | No duplicate VINs |
| Validity | 99%+ | 5 mileage anomalies, 0 invalid VINs |
| Consistency | ~85% | Lights/Grade missing correlated with no report |
| Timeliness | Single snapshot | One extract date (2026-06-09) |

---

*Generated for VIN Intelligence & Car Market Analytics Platform*
