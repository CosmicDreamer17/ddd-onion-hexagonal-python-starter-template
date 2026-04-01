.PHONY: install test lint format arch-check deps-check all-checks verify serve docker-build docker-run

verify: all-checks

install:
	uv sync

test:
	uv run python -m pytest

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

docker-build:
	docker build -t ddd-starter .

docker-run:
	docker run --rm -p 8000:8000 -v ddd-starter-data:/app/data ddd-starter
