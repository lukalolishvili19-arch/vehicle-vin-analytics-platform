# ETL Pipeline

End-to-end Python ETL for vehicle VIN auction data.

## Stack

- **pandas** / **numpy** — data processing
- **sqlalchemy** + **pymysql** — MySQL load
- **pyyaml** / **python-dotenv** — configuration

## Run

```bash
pip install -r requirements.txt
python -m etl
set LOAD_TO_MYSQL=true && python -m etl
```

## Modules

| Module | Purpose |
|--------|---------|
| `extract/` | CSV read, metadata |
| `validate/` | VIN rules, quarantine, IQR anomalies |
| `transform/` | Medallion bronze/silver/gold |
| `load/` | SQLAlchemy → MySQL star schema |
| `pipeline/` | Orchestrator + logging |
