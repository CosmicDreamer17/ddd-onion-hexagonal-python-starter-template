# DDD Onion Hexagonal Python Starter Template

## Architectural Doctrine

This repository implements **Domain-Driven Design (DDD)**, **Onion Architecture**, and **Hexagonal Architecture (Ports and Adapters)** with strict enforcement.

### Layer Rules

- **Domain** (`src/*/domain/`): Pure Python only. No framework imports. Contains entities, value objects, exceptions, and repository port interfaces.
- **Application** (`src/*/application/`): Orchestrates use cases and queries. Imports domain layer only. Defines context-specific Unit of Work ports, query ports, and read models.
- **Infrastructure** (`src/*/infrastructure/`): SQLAlchemy ORM models, concrete repositories, concrete UoW, query adapters, FastAPI routers. Imports application and domain layers.
- **Dependencies point inward**: infrastructure -> application -> domain. Never the reverse.

### Bounded Contexts

Two isolated bounded contexts: `work_management` and `integration_management`.

- Contexts must **never** import from each other.
- No shared database tables or foreign keys between contexts.
- Cross-context communication would use events or an anti-corruption layer (not implemented in this starter).

### Key Patterns

- **Entities**: `@dataclass(slots=True)` with factory `create()` classmethod. State transitions enforced through domain methods that raise domain-specific exceptions.
- **Ports**: `abc.ABC` classes in domain layer defining repository interfaces.
- **Adapters**: Concrete implementations in infrastructure layer (prefixed with `SqlAlchemy`).
- **Unit of Work**: Abstract in `shared/application/unit_of_work.py`. Context-specific UoW ports in each context's `application/use_cases.py`. One use case = one transaction.
- **Repositories**: Must explicitly map between ORM models and domain entities. No ORM leakage into domain.
- **Exceptions**: All domain exceptions extend a context-specific base error and end with `Error` suffix. Use domain-specific "not found" errors (e.g., `WorkItemNotFoundError`), never generic `ValueError`.

### CQRS Query Pattern

Read and write sides are separated:

- **Read models** (`application/read_models.py`): Frozen dataclasses for query responses. No invariant enforcement, no mutation methods.
- **Query ports** (`application/queries.py`): Abstract interfaces for read-only operations (`get_by_id`, `list_by_status`).
- **Query adapters** (`infrastructure/query_adapters.py`): SQLAlchemy implementations that map ORM rows directly to read models.
- **Query functions**: Thin wrappers that accept a query port and return read models. They never commit or modify data.

### API Layer (FastAPI)

REST endpoints are infrastructure adapters in `infrastructure/api.py`:

- Router factories accept UoW and query adapter instances (dependency injection via function args).
- Pydantic request/response schemas are defined in the API module, separate from domain entities.
- Domain exceptions are caught and mapped to HTTP status codes: `NotFoundError` -> 404, `InvalidStateTransitionError` -> 409, `InvalidOwnerEmailError` -> 422.
- Route handlers delegate to use cases or query functions. No business logic in the API layer.

## Development Commands

```bash
make install        # Install dependencies with uv
make test           # Run pytest
make lint           # Run ruff check + format check
make format         # Auto-format with ruff
make arch-check     # Run import-linter (static layer enforcement)
make deps-check     # Run deptry (dependency hygiene)
make all-checks     # Run all of the above
make serve          # Run FastAPI dev server with uvicorn --reload
```

## Workflow Rules

- Always run `make all-checks` before declaring any task complete.
- Keep edits surgical and localized. Do not refactor unrelated files.
- When adding new entities, follow the existing pattern: value_objects.py -> exceptions.py -> entities.py -> ports.py -> use_cases.py -> read_models.py -> queries.py -> orm.py -> repositories.py -> query_adapters.py -> unit_of_work.py -> api.py -> tests.
- Do not create generic "utils" or "helpers" modules.

## Architecture Enforcement

Three automated enforcement mechanisms:

1. **import-linter** (`.importlinter`): Static dependency graph validation. Layers contract + independence contract.
2. **pytest-archon** (`tests/architecture/test_architecture.py`): Dynamic architecture tests verifying domain purity and context isolation.
3. **deptry**: Ensures no missing, unused, or transitive dependency leaks in `pyproject.toml`.
