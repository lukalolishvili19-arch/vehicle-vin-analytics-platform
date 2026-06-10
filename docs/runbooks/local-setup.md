# Local Setup Runbook

<!-- TODO: Step-by-step local environment setup -->

## Prerequisites

- Python 3.11+
- Docker Desktop
- Git

## Steps

1. Copy `.env.example` to `.env`
2. Run `docker compose up -d`
3. Install Python dependencies: `pip install -e ".[dev]"`
4. Place source CSV in `data/raw/vehicle_search/`
5. Run `make pipeline`
