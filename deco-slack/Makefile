.PHONY: test format lint

test:
	poetry run python -m pytest tests/ --verbose

format:
	poetry run ruff format .

lint:
	poetry run ruff check . --fix