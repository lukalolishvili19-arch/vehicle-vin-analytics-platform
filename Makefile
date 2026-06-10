.PHONY: setup pipeline dbt-run dbt-test test lint excel mysql-init

setup:
	docker compose up -d

pipeline:
	python -m etl

pipeline-mysql:
	set LOAD_TO_MYSQL=true && python -m etl

excel:
	python excel/generate_workbook.py

test:
	pytest tests/ -v

lint:
	ruff check etl/ tests/
