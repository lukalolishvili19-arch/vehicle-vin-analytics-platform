# Architecture — VIN Intelligence Platform

## System Context

```
┌──────────────┐     ┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  CSV Source  │────▶│  ETL /etl   │────▶│  MySQL 8.0   │────▶│  Analytics  │
│  (Auction)   │     │  Python     │     │  Star Schema │     │  SQL/Excel  │
└──────────────┘     └──────┬──────┘     └──────┬───────┘     │  Power BI   │
                            │                    │             └─────────────┘
                            ▼                    ▼
                     Medallion Files       audit_pipeline_run
                     bronze/silver/gold    data quality logs
```

## ETL Pipeline (`/etl`)

| Stage | Module | Output |
|-------|--------|--------|
| Extract | `extract/csv_extractor.py` | landing CSV |
| Validate | `validate/rules.py`, `validate/vin.py` | valid + quarantine |
| Transform | `transform/medallion.py` | bronze → silver → gold |
| Anomalies | `validate/anomalies.py` | IQR outlier flags |
| Load | `load/loader.py` | MySQL warehouse |

**Stack:** pandas, numpy, sqlalchemy, pymysql

## Data Warehouse (MySQL)

- **Staging:** `stg_vehicle_search`, quarantine table
- **Dimensions:** vehicle (SCD2), make_model, color, auction_light, snapshot
- **Facts:** `fct_vehicle_inventory` (grain: VIN × snapshot)
- **Bridge:** `bridge_vehicle_lights`

## Analytics Layers

| Layer | Tool | Location |
|-------|------|----------|
| SQL | MySQL | `sql/analytics/` |
| Excel | openpyxl | `excel/output/` |
| Power BI | Desktop | `powerbi/` |

## Design Decisions

1. **Grade over Price** — no price in source; Grade is condition proxy
2. **Picture Count over image URL** — no URLs in source
3. **WMI for geography** — VIN prefix, not dealer location
4. **Style for drivetrain** — xDrive/sDrive parsed from trim
5. **Quarantine pattern** — bad VINs never reach facts

See ADRs in `docs/architecture/adr/`.
