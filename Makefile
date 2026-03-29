.PHONY: install test lint format arch-check deps-check all-checks serve

install:
	uv sync

test:
	uv run pytest

lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

arch-check:
	uv run lint-imports

deps-check:
	uv run deptry src/

all-checks: lint test arch-check deps-check

serve:
	uv run uvicorn shared.infrastructure.app:create_app --factory --reload
