# Medallion Design

<!-- TODO: Define layer contracts and schemas -->

## Layers

| Layer | Format | Purpose |
|-------|--------|---------|
| Raw | CSV | Immutable source copy |
| Landing | CSV/Parquet | Post-extract with metadata |
| Bronze | Parquet | Validated, schema-on-read |
| Silver | Parquet | Cleaned, typed, deduplicated |
| Gold | Parquet | Business-ready aggregates |
