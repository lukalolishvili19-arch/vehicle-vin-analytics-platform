# Installation Guide

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Docker Desktop | Latest |
| Git | Latest |
| Power BI Desktop | Optional (for dashboards) |
| MySQL Client | Optional (for ad-hoc SQL) |

---

## Step 1 — Clone Repository

```bash
git clone <your-repo-url>
cd vehicle-vin-analytics-platform
```

---

## Step 2 — Python Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
pip install -e .
```

Verify:

```bash
python -m etl --help
```

---

## Step 3 — Environment Variables

Copy template:

```bash
copy .env.example .env
```

Edit `.env`:

```env
APP_ENV=dev
LOG_LEVEL=INFO
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=vehicle_analytics
MYSQL_USER=vehicle_user
MYSQL_PASSWORD=changeme
LOAD_TO_MYSQL=false
```

Set `LOAD_TO_MYSQL=true` after MySQL is running to load warehouse tables.

---

## Step 4 — MySQL Database

### Docker (recommended)

```bash
docker compose up -d
docker compose ps
```

Wait for healthy status. Schema scripts in `sql/ddl/mysql/` apply automatically on first run.

### Manual init (if needed)

```bash
mysql -h localhost -u vehicle_user -pchangeme < sql/ddl/mysql/001_create_database.sql
mysql -h localhost -u vehicle_user -pchangeme vehicle_analytics < sql/ddl/mysql/002_create_reference.sql
# ... through 007_create_views.sql
```

---

## Step 5 — Source Data

Place CSV in raw zone:

```
data/raw/vehicle_search/edge_pipeline_vehicle_search_2026-06-09.csv
```

Expected columns: Picture Count, Stock Number, Year, Make, Model, Style, Exterior Color, Mileage, Has Condition Report, Grade, Lights, Announcements, Vin.

---

## Step 6 — Run ETL Pipeline

```bash
# Medallion file layers only
python -m etl

# With MySQL load
set LOAD_TO_MYSQL=true
python -m etl
```

Expected output:

```
rows_extracted: 555
rows_valid: 555
rows_quarantined: 0
bronze_file: data/bronze/vehicle_search/bronze_*.csv
silver_file: data/silver/vehicle_search/silver_*.csv
gold_file: data/gold/vehicle_search/gold_*.csv
```

---

## Step 7 — SQL Analytics

```bash
mysql -u vehicle_user -pchangeme vehicle_analytics < sql/analytics/10_executive_kpi_dashboard.sql
```

---

## Step 8 — Excel Report

```bash
python excel/generate_workbook.py
```

Output: `excel/output/vehicle_analytics.xlsx`

---

## Step 9 — Power BI

1. Open Power BI Desktop
2. Get Data → MySQL → `localhost:3306` / `vehicle_analytics`
3. Load fact + dimension tables (see `powerbi/star-schema.md`)
4. Import DAX from `powerbi/dax-measures.dax`
5. Build 5 pages per `powerbi/dashboard-pages.md`

---

## Step 10 — Run Tests

```bash
pytest tests/unit/ -v
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MySQL connection refused | `docker compose up -d`, check port 3306 |
| No CSV found | Copy file to `data/raw/vehicle_search/` |
| Module not found | `pip install -e .` from project root |
| LOAD_TO_MYSQL fails | Run DDL scripts first; check credentials |

---

## Next Steps

- Schedule ETL via Airflow (`orchestration/airflow/`)
- Add sale price from external API
- Deploy MySQL to cloud (RDS / Azure Database)
