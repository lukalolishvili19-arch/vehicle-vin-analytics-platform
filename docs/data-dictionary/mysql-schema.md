# MySQL Warehouse Schema

Schema design for the BMW vehicle auction / VIN inventory dataset (`edge_pipeline_vehicle_search`).

## Database

| Database | Purpose |
|----------|---------|
| `vehicle_analytics` | Single database, multiple logical schemas via table prefixes |

## Table Layers

```
ref_*           Reference / seed data
stg_*           Staging (raw ETL load)
dim_*           Dimensions
fct_*           Facts
bridge_*        Many-to-many relationships
audit_*         Pipeline & data quality metadata
vw_*            BI-facing views
```

## Star Schema

```
                    dim_make_model
                          │
                    dim_exterior_color
                          │
dim_vehicle ──────────────┼───────────── fct_vehicle_inventory
                          │                    │
                    bridge_vehicle_lights      │
                          │                    │
                    dim_auction_light          │
                                             dim_inventory_snapshot
```

## Grain

- **Fact table:** one row per `vin` per `snapshot_date`
- **Natural key:** `vin` (CHAR(17), validated unique)
- **Alternate key:** `stock_number`

## Source Column Mapping

| CSV Column | Target |
|------------|--------|
| Picture Count | `fct_vehicle_inventory.picture_count` | No `image_url` in source — photo count only |
| Stock Number | `dim_vehicle.stock_number` |
| Year | `dim_vehicle.model_year` |
| Make | `dim_make_model.make` |
| Model | `dim_make_model.model` |
| Style | `dim_vehicle.style` |
| Exterior Color | `dim_exterior_color.color_name` |
| Mileage | `fct_vehicle_inventory.mileage` |
| Has Condition Report | `fct_vehicle_inventory.has_condition_report` |
| Grade | `fct_vehicle_inventory.grade` |
| Lights | `dim_auction_light` + `bridge_vehicle_lights` |
| Announcements | `fct_vehicle_inventory.announcements` + derived flags |
| Vin | `dim_vehicle.vin` |

## Derived Columns (ETL)

From `Announcements` text:

| Column | Rule |
|--------|------|
| `is_as_is` | contains "AS IS" |
| `is_inop` | contains "INOP" |
| `has_structural_damage` | contains "STRUCTURAL" |
| `is_salvage` | contains "SALVAGE" or "TOTAL LOSS" |
| `is_repo` | contains "REPO" |
| `is_green_light` | contains "GREEN LIGHT" |

From `Mileage`:

| Column | Rule |
|--------|------|
| `mileage_bucket` | Low (<30k), Medium (30k–100k), High (>100k) |
| `is_mileage_anomaly` | mileage IN (0, 1) |

From `Lights`:

| Column | Rule |
|--------|------|
| `primary_light` | first value before comma |
| Secondary lights | `bridge_vehicle_lights` rows |

## Data Quality Rules

| Rule | Action |
|------|--------|
| VIN length != 17 | Reject → quarantine |
| VIN duplicate | Reject → quarantine |
| Year not in 1990–2030 | Reject → quarantine |
| Grade not in 0.0–5.0 | Set NULL + audit log |
| Mileage < 0 | Reject → quarantine |
| Missing Style | Allow NULL |
| Missing Grade | Allow NULL |
| Missing Lights | Set `Unknown` |

## Indexes Strategy

- PK on all surrogate keys (`BIGINT UNSIGNED AUTO_INCREMENT`)
- UNIQUE on `dim_vehicle.vin`
- UNIQUE on `(vin, snapshot_date)` in fact table
- Index on `model_year`, `make`, `model`, `grade`, `primary_light_id`

## Charset

- `utf8mb4` / `utf8mb4_unicode_ci` for international text in announcements
