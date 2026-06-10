#!/usr/bin/env bash
# Run full ETL pipeline
# TODO: Implement run_pipeline.sh

set -euo pipefail
python -m src.pipelines.run_full_pipeline
