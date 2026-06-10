# Data Flow

<!-- TODO: Document end-to-end data movement -->

## Pipeline Stages

1. **Source** → `data/raw/vehicle_search/`
2. **Landing** → `data/landing/vehicle_search/`
3. **Bronze** → validated raw (Parquet)
4. **Silver** → cleaned, deduplicated
5. **Gold** → business aggregates
6. **Warehouse** → PostgreSQL via dbt
7. **BI** → Metabase
