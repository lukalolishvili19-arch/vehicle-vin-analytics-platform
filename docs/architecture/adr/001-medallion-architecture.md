# ADR 001: Medallion Architecture

## Status

Accepted

## Context

Vehicle CSV data requires staged processing with quarantine for bad records.

## Decision

Adopt Bronze / Silver / Gold medallion pattern on local file storage.

## Consequences

- Clear separation of raw vs cleaned data
- Enables replay and audit trails
