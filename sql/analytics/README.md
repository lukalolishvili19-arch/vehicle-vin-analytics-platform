# SQL Analytics Index

Professional business queries for **VIN Intelligence & Car Market Analytics Platform**.

> **Important:** Source data has no price, fuel type, or dealer geography.  
> Queries use **Grade** (condition), **Mileage**, **Lights**, and **Announcements** as market proxies.

| File | Purpose | Techniques |
|------|---------|------------|
| `01_grade_analysis_by_model_year.sql` | Grade by model/year | CTE, GROUP BY |
| `02_market_share_by_model.sql` | Model inventory share | CTE, window RANK |
| `03_mileage_vs_grade_correlation.sql` | Mileage vs quality | CTE, STDDEV, segments |
| `04_drivetrain_distribution.sql` | AWD/RWD from Style | CASE, window % |
| `05_condition_report_analysis.sql` | Report coverage | CTE, conditional agg |
| `06_auction_lights_summary.sql` | Light signal distribution | JOIN bridge, DISTINCT |
| `07_top_vehicles_by_grade.sql` | Best units ranking | ROW_NUMBER |
| `08_bottom_risk_vehicles.sql` | High-risk inventory | ROW_NUMBER, filters |
| `09_vin_wmi_region_analysis.sql` | VIN origin proxy | JOIN ref_vin_wmi |
| `10_executive_kpi_dashboard.sql` | Executive KPIs | Single-row aggregate |

## Run

```bash
mysql -u vehicle_user -p vehicle_analytics < sql/analytics/10_executive_kpi_dashboard.sql
```
