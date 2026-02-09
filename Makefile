.PHONY: install test lint format clean

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=claude_env_sync --cov-report=term-missing

test-unit:
	pytest tests/unit/ -v --cov=claude_env_sync --cov-report=term-missing

test-integration:
	pytest tests/integration/ -v

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

clean:
	rm -rf dist/ build/ *.egg-info .pytest_cache .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
