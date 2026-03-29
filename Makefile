.PHONY: install test lint format arch-check deps-check all-checks docker-build docker-run

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

docker-build:
	docker build -t ddd-starter .

docker-run:
	docker run --rm ddd-starter
