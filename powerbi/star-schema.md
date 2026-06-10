# Power BI — Star Schema Model

## Data Source

Connect Power BI Desktop to MySQL:

```
Server: localhost:3306
Database: vehicle_analytics
```

Or import from `data/gold/vehicle_search/gold_*.csv` for offline demo.

---

## Star Schema

```
dim_inventory_snapshot ──< fct_vehicle_inventory >── dim_vehicle
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
            dim_make_model  dim_exterior_color  dim_auction_light
                              │
                    bridge_vehicle_lights >── dim_auction_light
```

### Fact Table: `fct_vehicle_inventory`
- **Grain:** 1 row per VIN per snapshot
- **Measures:** mileage, grade, picture_count, flags

### Dimensions
| Table | Role |
|-------|------|
| `dim_vehicle` | VIN attributes, SCD2 |
| `dim_make_model` | Make / model hierarchy |
| `dim_exterior_color` | Color lookup |
| `dim_auction_light` | Light codes |
| `dim_inventory_snapshot` | Snapshot date |

---

## Relationships

| From | To | Cardinality | Cross-filter |
|------|-----|-------------|--------------|
| fct_vehicle_inventory[snapshot_key] | dim_inventory_snapshot[snapshot_key] | Many:One | Single |
| fct_vehicle_inventory[vehicle_key] | dim_vehicle[vehicle_key] | Many:One | Single |
| fct_vehicle_inventory[make_model_key] | dim_make_model[make_model_key] | Many:One | Single |
| fct_vehicle_inventory[color_key] | dim_exterior_color[color_key] | Many:One | Single |
| fct_vehicle_inventory[primary_light_key] | dim_auction_light[light_key] | Many:One | Single |
| bridge_vehicle_lights[inventory_key] | fct_vehicle_inventory[inventory_key] | Many:One | Both |

---

## Calculated Columns

```dax
// Vehicle age at snapshot
Vehicle Age = fct_vehicle_inventory[vehicle_age]

// Risk score (higher = riskier)
Risk Score =
    fct_vehicle_inventory[is_as_is] * 3
    + fct_vehicle_inventory[has_structural_damage] * 5
    + fct_vehicle_inventory[is_salvage] * 4
    + fct_vehicle_inventory[is_inop] * 3
    + IF(fct_vehicle_inventory[primary_light_key] = 1, 2, 0)

// Grade tier sort order
Grade Tier Order =
    SWITCH(
        fct_vehicle_inventory[grade_tier],
        "EXCELLENT", 1,
        "GOOD", 2,
        "FAIR", 3,
        "POOR", 4,
        5
    )

// Listing completeness (photos proxy — no image URL in source)
Listing Completeness =
    IF(fct_vehicle_inventory[picture_count] = 0, "No Photos",
    IF(fct_vehicle_inventory[picture_count] < 10, "Low Photos", "Good Photos"))
```

---

## DAX Measures

```dax
Total Vehicles = COUNTROWS(fct_vehicle_inventory)

Total Models = DISTINCTCOUNT(fct_vehicle_inventory[model])

Avg Mileage = AVERAGE(fct_vehicle_inventory[mileage])

Avg Grade =
    CALCULATE(
        AVERAGE(fct_vehicle_inventory[grade]),
        NOT(ISBLANK(fct_vehicle_inventory[grade]))
    )

Condition Report % =
    DIVIDE(
        SUM(fct_vehicle_inventory[has_condition_report]),
        [Total Vehicles]
    )

Green Light % =
    DIVIDE(
        CALCULATE([Total Vehicles], dim_auction_light[light_code] = "GREEN"),
        [Total Vehicles]
    )

AS IS Count =
    CALCULATE([Total Vehicles], fct_vehicle_inventory[is_as_is] = 1)

High Risk Count =
    CALCULATE(
        [Total Vehicles],
        fct_vehicle_inventory[has_structural_damage] = 1
            || fct_vehicle_inventory[is_salvage] = 1
    )

Model Share % =
    DIVIDE(
        [Total Vehicles],
        CALCULATE([Total Vehicles], ALL(dim_make_model[model]))
    )

Avg Grade by Model =
    CALCULATE([Avg Grade], ALLEXCEPT(dim_make_model, dim_make_model[model]))

Top Grade Rank =
    RANKX(
        ALL(dim_make_model[model]),
        [Avg Grade by Model],
        ,
        DESC
    )
```

---

## Dashboard Pages

See `powerbi/dashboard-pages.md` for layout specifications.

Import template: connect MySQL → load star schema tables → paste DAX from `powerbi/dax-measures.dax`.
