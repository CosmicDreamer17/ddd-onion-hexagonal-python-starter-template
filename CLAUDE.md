# DDD Onion Hexagonal Python Starter Template

## Architectural Doctrine

This repository implements **Domain-Driven Design (DDD)**, **Onion Architecture**, and **Hexagonal Architecture (Ports and Adapters)** with strict enforcement.

### Layer Rules

- **Domain** (`src/*/domain/`): Pure Python only. No framework imports. Contains entities, value objects, exceptions, and repository port interfaces.
- **Application** (`src/*/application/`): Orchestrates use cases. Imports domain layer only. Defines context-specific Unit of Work ports.
- **Infrastructure** (`src/*/infrastructure/`): SQLAlchemy ORM models, concrete repositories, concrete UoW. Imports application and domain layers.
- **Dependencies point inward**: infrastructure → application → domain. Never the reverse.

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
- **Exceptions**: All domain exceptions extend a context-specific base error and end with `Error` suffix.

## Development Commands

```bash
make install        # Install dependencies with uv
make test           # Run pytest
make lint           # Run ruff check + format check
make format         # Auto-format with ruff
make arch-check     # Run import-linter (static layer enforcement)
make deps-check     # Run deptry (dependency hygiene)
make all-checks     # Run all of the above
```

## Workflow Rules

- Always run `make all-checks` before declaring any task complete.
- Keep edits surgical and localized. Do not refactor unrelated files.
- When adding new entities, follow the existing pattern: value_objects.py → exceptions.py → entities.py → ports.py → use_cases.py → orm.py → repositories.py → unit_of_work.py → tests.
- Do not create generic "utils" or "helpers" modules.

## Architecture Enforcement

Three automated enforcement mechanisms:

1. **import-linter** (`.importlinter`): Static dependency graph validation. Layers contract + independence contract.
2. **pytest-archon** (`tests/architecture/test_architecture.py`): Dynamic architecture tests verifying domain purity and context isolation.
3. **deptry**: Ensures no missing, unused, or transitive dependency leaks in `pyproject.toml`.
