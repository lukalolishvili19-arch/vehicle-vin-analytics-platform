# BI Refresh Runbook

<!-- TODO: Steps to refresh Metabase dashboards after pipeline run -->

## After Pipeline Success

1. Confirm dbt marts built: `make dbt-test`
2. Open Metabase → sync database schema
3. Verify dashboard freshness timestamps
