# ADR 003: Orchestration Choice

## Status

Accepted

## Context

Pipeline has multiple dependent stages (ingest → transform → dbt → notify).

## Decision

Use Apache Airflow for workflow orchestration.

## Consequences

- Industry-standard scheduling and retries
- DAG-based dependency management
