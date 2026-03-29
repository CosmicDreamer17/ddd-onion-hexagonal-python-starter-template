# DDD Onion Hexagonal Starter Template

This is a **starter template** for Python backend applications. The two bounded contexts (`work_management`, `integration_management`) are working examples that demonstrate every pattern. When building a real application, add new contexts with `/add-context` or adapt the existing ones. See @CONTRIBUTING.md for step-by-step guides.

## Architecture Rules

- **Dependencies point inward**: infrastructure → application → domain. Never the reverse.
- **Domain layer** (`src/*/domain/`): Pure Python only. NO framework imports. NO imports from application or infrastructure.
- **Application layer** (`src/*/application/`): Imports domain only. NO infrastructure imports.
- **Bounded contexts** (`work_management`, `integration_management`): NEVER import from each other.

## Commands

```bash
make all-checks   # ALWAYS run before declaring done (lint + test + arch-check + deps-check)
make test          # pytest
make lint          # ruff check + format
make arch-check    # import-linter (layer + independence contracts)
make serve         # FastAPI dev server
```

## Patterns

- **Entities**: `@dataclass(slots=True)` with `create()` classmethod. Invariants enforced in domain methods.
- **Exceptions**: Extend context base error. Use `Error` suffix. Use `*NotFoundError` for missing entities, never `ValueError`.
- **Ports**: `abc.ABC` with `@abstractmethod` in domain layer.
- **Adapters**: `SqlAlchemy` prefix. Explicit `_to_domain()` and `_to_model()` mapping. ORM never leaks into domain.
- **Use cases**: Plain functions. First arg is UoW. One function = one transaction. `with uow:` → logic → `uow.commit()`.
- **Read models**: `@dataclass(frozen=True, slots=True)`. Separate from domain entities.
- **Query ports**: `abc.ABC` in application layer. Query adapters in infrastructure.
- **API routes**: FastAPI routers in infrastructure. Pydantic schemas separate from domain. Catch domain exceptions → HTTP status codes (404/409/422).
- **Domain events**: Dataclasses in `shared/domain/events.py`. Published via `EventBus` protocol. Handlers registered in app factory.

## File Creation Order

When adding new features: value_objects.py → exceptions.py → entities.py → ports.py → use_cases.py → read_models.py → queries.py → orm.py → repositories.py → query_adapters.py → unit_of_work.py → api.py → tests

## Skills

- `/fix-issue <number>` — Fix a GitHub issue following project patterns
- `/add-entity <context> <entity>` — Add a new entity to a bounded context
- `/add-context <name>` — Add a new bounded context
