# DataGrip — MySQL Connection

## Connection Settings

| Field | Value |
|-------|-------|
| **Host** | `localhost` |
| **Port** | `3306` |
| **Database** | `vehicle_analytics` |
| **User** | `vehicle_user` |
| **Password** | `changeme` |
| **Driver** | MySQL (8+) |

## Setup Steps

1. Open **DataGrip**
2. **+** → **Data Source** → **MySQL** (NOT Amazon Aurora)
3. **General** tab — fill exactly:

| Field | Value | ⚠️ Common mistake |
|-------|-------|-------------------|
| Name | `vehicle_analytics` | Any name is OK |
| Host | `localhost` | Not 127.0.0.1 required, both work |
| Port | `3306` | |
| **User** | `vehicle_user` | **NOT** your Windows name (`Ideapad Pro5i`) |
| **Password** | `changeme` | Must be filled — `using password: NO` = empty password |
| Database | `vehicle_analytics` | |

4. **Advanced** tab → disable **Aurora** / AWS plugins if present
5. **Driver**: MySQL (8+) — click **Download** if missing
6. **Test Connection** → ✅ Successful → **OK**

## Fix: `Access denied for user 'Ideapad Pro5i'@'...' (using password: NO)`

This means DataGrip used your **Windows username** with **no password**.

- Clear the User field and type: `vehicle_user`
- Enter Password: `changeme`
- Check **Save password**
- Do NOT use "OS Authentication" / Windows auth

## Fix: Aurora plugin timeout

You selected **Amazon Aurora** instead of **MySQL**.

- Delete the data source
- Create new: **Data Source → MySQL** (plain MySQL)
- URL should look like: `jdbc:mysql://localhost:3306/vehicle_analytics`

## Verify Data

```sql
USE vehicle_analytics;

-- ✅ Recommended: latest snapshot only (always 555)
SELECT COUNT(*) AS total FROM vw_vehicle_inventory_current;

-- Or raw fact table (555 if one snapshot; 1110 if two load dates exist)
SELECT COUNT(*) AS total FROM fct_vehicle_inventory;

-- See all snapshots
SELECT snapshot_key, snapshot_date, valid_records
FROM dim_inventory_snapshot
ORDER BY snapshot_date;
```

> **Why 1110?** Fact table grain = **one row per VIN per snapshot date**.
> Loading on June 9 and June 10 → 555 + 555 = 1110. This is correct star-schema behavior.
> For BI and thesis demo use `vw_vehicle_inventory_current` or latest `snapshot_date`.

### Clean up old snapshots (optional)

```powershell
python scripts/mysql_cleanup_old_snapshots.py
```

Then `SELECT COUNT(*) FROM fct_vehicle_inventory` → 555.

```sql
SELECT model, COUNT(*) AS cnt
FROM vw_vehicle_inventory_current
GROUP BY model
ORDER BY cnt DESC
LIMIT 10;
```

## Key Tables

| Table | Purpose |
|-------|---------|
| `fct_vehicle_inventory` | Main fact (555 rows) |
| `dim_vehicle` | VIN dimension |
| `dim_make_model` | Model hierarchy |
| `vw_vehicle_inventory_current` | BI-ready view |

## Docker must be running

```powershell
docker compose ps
# vehicle_analytics_mysql should be Up (healthy)
```

If connection fails: `docker compose up -d` from project root.
