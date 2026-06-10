# Power BI — Quick Import Guide

## Option A: CSV (fastest — no MySQL required)

1. Run ETL: `python scripts/run_etl_stdlib.py`
2. Open **Power BI Desktop**
3. **Get Data** → **Text/CSV** → select:
   ```
   powerbi/data/fct_vehicle_inventory.csv
   ```
4. **Transform Data** → set types (grade=decimal, mileage=whole number)
5. Copy measures from `powerbi/dax-measures.dax`
6. Build 5 pages per `powerbi/dashboard-pages.md`

## Option B: MySQL (production)

1. `docker compose up -d`
2. `set LOAD_TO_MYSQL=true && python -m etl`
3. Power BI → **Get Data** → **MySQL database**
   - Server: `localhost:3306`
   - Database: `vehicle_analytics`
   - Tables: `fct_vehicle_inventory`, `dim_*`, `bridge_vehicle_lights`
4. Model star schema per `powerbi/star-schema.md`

## Template PBIX

Create new PBIX and save as `powerbi/VIN_Analytics.pbix` after connecting data.

## Screenshots

Export page PNGs to `docs/screenshots/pbi_page1_executive.png` etc.
