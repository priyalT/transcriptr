lint:
	ruff check src tests
	ruff format --check src tests

format:
	ruff format src tests

type-check:
	mypy src

test:
	pytest

test-integration:
	pytest -m integration

coverage:
	pytest --cov=transcriptr --cov-report=term-missing