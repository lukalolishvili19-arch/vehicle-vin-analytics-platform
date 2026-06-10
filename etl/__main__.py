"""CLI entry point: python -m etl"""

from __future__ import annotations

import argparse
from pathlib import Path

from etl.config import load_config
from etl.pipeline.runner import run_pipeline
from etl.utils.logging_setup import setup_logging


def main() -> None:
    parser = argparse.ArgumentParser(description="Vehicle VIN Analytics ETL Pipeline")
    parser.add_argument("--env", default=None, help="Environment (dev/staging/prod)")
    parser.add_argument("--source", default=None, help="Path to source CSV file")
    args = parser.parse_args()

    cfg = load_config(args.env)
    setup_logging(cfg.log_level)

    source = Path(args.source) if args.source else None
    result = run_pipeline(source_path=source, config=cfg)

    print("\n--- ETL Pipeline Summary ---")
    for key, value in result.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
