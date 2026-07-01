lint:
	uv run ruff check src tests
	uv run ruff format --check src tests

format:
	uv run ruff format src tests

type-check:
	uv run mypy src

test:
	uv run pytest

test-integration:
	uv run pytest -m integration

coverage:
	uv run pytest --cov=transcriptr --cov-report=term-missing