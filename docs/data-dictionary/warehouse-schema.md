# Warehouse Schema

<!-- TODO: Document star schema after dbt implementation -->

## Schemas

- `staging` — raw loads from ETL
- `intermediate` — enriched transformations
- `marts` — dimensions, facts, aggregates

## Star Schema

- `dim_vehicle`
- `dim_make_model`
- `fct_vehicle_inventory`
