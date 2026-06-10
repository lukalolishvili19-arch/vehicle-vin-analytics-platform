# GitHub Setup

## First-time push

```powershell
cd C:\Users\Ideapad Pro5i\Projects\vehicle-vin-analytics-platform

git init
git branch -M main
git add .
git commit -m "feat: VIN Intelligence platform — ETL, MySQL, Power BI, Docker"

# Option A — GitHub CLI
gh repo create vin-intelligence-analytics --public --description "VIN Intelligence & Car Market Analytics Platform" --source=. --push

# Option B — manual remote
git remote add origin https://github.com/YOUR_USERNAME/vin-intelligence-analytics.git
git push -u origin main
```

## What gets committed

| Included | Excluded (.gitignore) |
|----------|----------------------|
| Source code (`etl/`, `sql/`, `powerbi/`) | `.env` secrets |
| DDL scripts | `data/bronze`, `silver` layers |
| Docs & README | MySQL data volumes |
| `powerbi/data/fct_vehicle_inventory.csv` (demo) | `docs/screenshots/pbi_*.png` |
| Sample fixtures in `tests/` | `excel/output/`, `*.pbix` |

## Repository description (copy to GitHub)

```
Production-ready data platform: BMW auction VIN inventory → Python ETL → MySQL star schema → Power BI dashboards. Medallion architecture, VIN validation, SQL analytics.
```

## Topics

`data-engineering` `etl` `mysql` `power-bi` `vin` `automotive` `python` `docker` `portfolio`
