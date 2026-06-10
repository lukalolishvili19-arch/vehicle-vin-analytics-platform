# Power BI Dashboard — ნაბიჯ-ნაბიჯ (ქართულად)

## მეთოდი A: CSV Import (რეკომენდებული — სწრაფი)

### 1. მონაცემების ექსპორტი

```powershell
cd C:\Users\Ideapad Pro5i\Projects\vehicle-vin-analytics-platform
python scripts\export_powerbi_data.py
```

ან უკვე არსებული: `powerbi/data/fct_vehicle_inventory.csv`

### 2. Power BI Desktop გახსენი

### 3. მონაცემების ჩატვირთვა

**Get data** → **Text/CSV** → აირჩიე:

```
powerbi\data\fct_vehicle_inventory.csv
```

**Transform Data** → შეცვალე ტიპები:
| სვეტი | ტიპი |
|-------|------|
| model_year, mileage, picture_count | Whole Number |
| grade | Decimal Number |
| has_condition_report, is_as_is | Whole Number |
| model, vin, primary_light | Text |

**Close & Apply**

### 4. DAX Measures (Modeling → New measure)

კოპირება `powerbi/dax-measures.dax`-დან — მინიმუმ ეს:

```dax
Total Vehicles = COUNTROWS(fct_vehicle_inventory)

Avg Mileage = AVERAGE(fct_vehicle_inventory[mileage])

Avg Grade = CALCULATE(AVERAGE(fct_vehicle_inventory[grade]), NOT(ISBLANK(fct_vehicle_inventory[grade])))

Condition Report % = DIVIDE(SUM(fct_vehicle_inventory[has_condition_report]), [Total Vehicles])

AS IS Count = CALCULATE(COUNTROWS(fct_vehicle_inventory), fct_vehicle_inventory[is_as_is] = 1)
```

---

## 5 გვერდი — რა ვიზუალი შექმნა

### გვერდი 1: Executive Overview

| ვიზუალი | ველი | ტიპი |
|---------|------|------|
| Card | Total Vehicles | Measure |
| Card | Avg Mileage | Measure |
| Card | Avg Grade | Measure |
| Card | Total Models | `DISTINCTCOUNT(model)` measure |
| Donut | primary_light | Count |
| Bar chart | model (Top 10) | Count of vin |
| Line | model_year | Avg Grade |

**Slicers:** model_year, mileage_bucket, has_condition_report

---

### გვერდი 2: Brand / Model Analysis

| ვიზუალი | ველი |
|---------|------|
| Treemap | model → Count |
| Clustered bar | model → Avg Grade |
| Table | model, vehicle count, avg_mileage, avg_grade |

ფილტრი: Top N models by count

---

### გვერდი 3: VIN Analysis

| ვიზუალი | ველი |
|---------|------|
| **Slicer (Search)** | vin |
| Table | vin, stock_number, model, style, grade, mileage, announcements |
| Histogram | grade (bins: 0-2, 2-3.5, 3.5-4.5, 4.5-5) |

---

### გვერდი 4: Quality & Mileage

| ვიზუალი | ველი |
|---------|------|
| Scatter | X=mileage, Y=grade, Size=picture_count |
| Column | mileage_bucket → Count |
| Line | model_year → Avg Mileage |

> Price არ არის მონაცემებში — Grade vs Mileage გამოიყენე.

---

### გვერდი 5: Risk & Insights

| ვიზუალი | ველი |
|---------|------|
| Card | AS IS Count |
| Card | Structural Damage (has_structural_damage) |
| Bar | primary_light → Count |
| Table | vin, model, grade, is_as_is, has_structural_damage, announcements |

ფილტრი: grade < 2.5 OR is_as_is = 1

---

## მეთოდი B: MySQL პირდაპირ

1. გახსენი `powerbi/VIN_Analytics.pbids` (ორმაგი კლიკი)
2. Password: `changeme`
3. აირჩიე: `fct_vehicle_inventory`, `dim_make_model`, `dim_auction_light`
4. Relationships (Model view):

```
fct_vehicle_inventory[make_model_key] → dim_make_model[make_model_key]
fct_vehicle_inventory[primary_light_key] → dim_auction_light[light_key]
```

---

## შენახვა

**File** → **Save as** → `powerbi/VIN_Analytics.pbix`

Screenshots → `docs/screenshots/pbi_page1.png` ...

---

## თემა

**View** → **Themes** → **Customize current theme**
- Primary: #1F4788 (BMW blue)
- Background: #F5F5F5
