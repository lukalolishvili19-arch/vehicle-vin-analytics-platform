# Pipeline Failure Recovery

<!-- TODO: Operational playbook for pipeline failures -->

## Common Failures

- **Validation errors** → Check `data/quarantine/vehicle_search/`
- **DB connection** → Verify Docker Postgres is running
- **dbt test failures** → Review `dbt/logs/`
