# Contributing Guide

## Getting Started

**Prerequisites**: Python 3.12+ and [uv](https://docs.astral.sh/uv/)

```bash
git clone https://github.com/CosmicDreamer17/ddd-onion-hexagonal-python-starter-template.git
cd ddd-onion-hexagonal-python-starter-template
make install      # Install dependencies
make all-checks   # Verify everything works
```

## Architecture Overview

This template uses three interconnected patterns:

- **DDD**: Business language drives naming. Two isolated bounded contexts.
- **Onion Architecture**: Dependencies point inward: infrastructure -> application -> domain.
- **Hexagonal Architecture**: Abstract ports (in domain/application) + concrete adapters (in infrastructure).

See the [README](README.md) for the visual layer diagram.

## Adding a New Bounded Context

Example: adding a `notification_management` context.

### 1. Create the directory structure

```
src/notification_management/
├── __init__.py
├── py.typed
├── domain/
│   ├── __init__.py
│   ├── value_objects.py    # Enums (e.g., NotificationChannel)
│   ├── exceptions.py       # NotificationManagementError base + specific errors
│   ├── entities.py          # Notification entity with @dataclass(slots=True)
│   └── ports.py             # NotificationRepository(abc.ABC)
├── application/
│   ├── __init__.py
│   ├── use_cases.py         # NotificationManagementUnitOfWork port + use case functions
│   ├── read_models.py       # NotificationReadModel (frozen dataclass)
│   └── queries.py           # NotificationQueryPort + query functions
└── infrastructure/
    ├── __init__.py
    ├── orm.py               # NotificationModel (SQLAlchemy)
    ├── repositories.py      # SqlAlchemyNotificationRepository
    ├── query_adapters.py    # SqlAlchemyNotificationQueryAdapter
    ├── unit_of_work.py      # SqlAlchemyNotificationManagementUnitOfWork
    └── api.py               # FastAPI router
```

### 2. Register in build configuration

**pyproject.toml** — add the package:
```toml
[tool.hatch.build.targets.wheel]
packages = [
    "src/work_management",
    "src/integration_management",
    "src/notification_management",  # Add this
    "src/shared",
]
```

### 3. Register in architecture enforcement

**.importlinter** — add layers contract and update independence:
```ini
[importlinter:contract:notification-management-layers]
name = Onion layer enforcement for notification_management
type = layers
layers =
    notification_management.infrastructure
    notification_management.application
    notification_management.domain

[importlinter:contract:bounded-context-independence]
name = Bounded context independence
type = independence
modules =
    work_management
    integration_management
    notification_management
```

**tests/architecture/test_architecture.py** — add isolation tests:
```python
def test_notification_management_does_not_import_others():
    (
        archrule("notification isolation")
        .match("notification_management")
        .match("notification_management.*")
        .should_not_import("work_management")
        .should_not_import("work_management.*")
        .should_not_import("integration_management")
        .should_not_import("integration_management.*")
        .check("notification_management")
    )
```

### 4. Wire into the application

**src/shared/infrastructure/app.py** — add the router:
```python
from notification_management.infrastructure.api import create_notification_management_router
from notification_management.infrastructure.query_adapters import SqlAlchemyNotificationQueryAdapter
from notification_management.infrastructure.unit_of_work import SqlAlchemyNotificationManagementUnitOfWork

# In create_app():
notification_uow = SqlAlchemyNotificationManagementUnitOfWork(engine)
notification_query = SqlAlchemyNotificationQueryAdapter(engine)
app.include_router(create_notification_management_router(notification_uow, notification_query))
```

### 5. Add tests

Create `tests/notification_management/` with:
- `__init__.py`
- `test_domain.py` — entity invariant tests
- `test_use_cases.py` — integration tests with real SQLite
- `test_queries.py` — query adapter tests
- `test_api.py` — API endpoint tests

### 6. Verify

```bash
make all-checks  # Must pass: lint, test, arch-check, deps-check
```

## Adding a New Entity to an Existing Context

Example: adding `Comment` to `work_management`.

1. **Define value objects** in `src/work_management/domain/value_objects.py` (if needed)
2. **Define exceptions** in `src/work_management/domain/exceptions.py`:
   ```python
   class CommentNotFoundError(WorkManagementError):
       def __init__(self, comment_id: object) -> None:
           super().__init__(f"Comment {comment_id} not found.")
   ```
3. **Define the entity** in `src/work_management/domain/entities.py` (or a new file if large):
   ```python
   @dataclass(slots=True)
   class Comment:
       id: uuid.UUID
       work_item_id: uuid.UUID
       text: str
       created_at: datetime

       @classmethod
       def create(cls, work_item_id: uuid.UUID, text: str) -> "Comment":
           return cls(id=uuid.uuid4(), work_item_id=work_item_id, text=text, created_at=datetime.now(UTC))
   ```
4. **Define the port** in `src/work_management/domain/ports.py`
5. **Add use cases** in `src/work_management/application/use_cases.py`
6. **Add read model** in `src/work_management/application/read_models.py`
7. **Add ORM model** in `src/work_management/infrastructure/orm.py`
8. **Add repository** in `src/work_management/infrastructure/repositories.py`
9. **Add API endpoints** in `src/work_management/infrastructure/api.py`
10. **Add tests** for domain, use cases, queries, and API
11. Run `make all-checks`

## Adding a New Infrastructure Adapter

To add a different persistence backend (e.g., PostgreSQL, Redis) or a new delivery mechanism (e.g., gRPC, CLI):

1. **The domain and application layers do not change.** Ports are already defined.
2. Create a new adapter in `infrastructure/` that implements the existing port interface.
3. Wire it in `shared/infrastructure/app.py` (or create a new composition root).

Example — adding a Redis cache adapter:
```python
# src/work_management/infrastructure/redis_cache.py
from work_management.application.queries import WorkItemQueryPort

class RedisWorkItemQueryAdapter(WorkItemQueryPort):
    def __init__(self, redis_client):
        self._redis = redis_client

    def get_by_id(self, item_id):
        # Check cache, fall back to DB
        ...
```

The architecture enforcement tools will verify the adapter stays in the infrastructure layer.

## Publishing Domain Events

Domain events enable cross-context communication without direct imports. See the existing `WorkItemCompletedEvent` for the full pattern.

1. **Define the event** in `src/{context}/domain/events.py`:
   ```python
   @dataclass(frozen=True, slots=True)
   class OrderPlacedEvent(DomainEvent):
       order_id: uuid.UUID = None  # type: ignore[assignment]
       total: float = 0.0
   ```

2. **Publish in a use case** (pass `event_bus` as optional parameter):
   ```python
   if event_bus is not None:
       event_bus.publish(OrderPlacedEvent(order_id=order.id, total=order.total))
   ```

3. **Handle in another context** (`src/{other_context}/application/event_handlers.py`):
   ```python
   def handle_order_placed(event: DomainEvent, uow: SomeUnitOfWork) -> None:
       # React without importing from the originating context
       order_id = getattr(event, "order_id", None)
       # ... create a fulfillment job, send a notification, etc.
   ```

4. **Wire in app factory** (`src/shared/infrastructure/app.py`):
   ```python
   event_bus.subscribe(OrderPlacedEvent, partial(handle_order_placed, uow=some_uow))
   ```

Key rule: handlers access event data via `getattr()` on the base `DomainEvent` type. They never import the event class from another context.

## Code Conventions

| Convention | Rule |
|-----------|------|
| Entities | `@dataclass(slots=True)` with `create()` factory classmethod |
| Ports | `abc.ABC` with `@abstractmethod` |
| Adapters | Prefix with `SqlAlchemy` (or adapter technology name) |
| Exceptions | Extend context base error, use `Error` suffix |
| Use cases | Plain functions, first arg is UoW, one function = one transaction |
| Read models | `@dataclass(frozen=True, slots=True)` — immutable |
| ORM mapping | Explicit `_to_domain()` and `_to_model()` static methods |
| Repos | Never call `commit()` or `rollback()` — that's the UoW's job |
| Not found | Use domain-specific `*NotFoundError`, never generic `ValueError` |

## Running Checks

| Command | What it validates |
|---------|-------------------|
| `make lint` | Code style and formatting (ruff) |
| `make test` | All pytest tests including architecture tests |
| `make arch-check` | Static import graph analysis (import-linter) — verifies layer direction and context isolation |
| `make deps-check` | Dependency hygiene (deptry) — no missing, unused, or transitive deps |
| `make all-checks` | All of the above in sequence |

**Always run `make all-checks` before pushing.**

## Claude Code Workflow

This template includes three agent personas in `.claude/agents/`:

1. **Planner** (`planner.md`): Analyzes requirements, produces implementation plans. Read-only — never modifies files.
2. **Implementer** (`implementer.md`): Writes code following architectural patterns. Must run `make all-checks` after changes.
3. **Reviewer** (`reviewer.md`): Audits for architecture violations, test coverage, and naming conventions.

Three skills provide guided workflows — invoke them directly:
- `/fix-issue <number>` — Fix a GitHub issue end-to-end
- `/add-entity <context> <entity>` — Add a new entity with all layers
- `/add-context <name>` — Scaffold an entire new bounded context

Path-scoped rules in `.claude/rules/` automatically load context based on which files are being edited:
- `domain-rules.md` — activates when editing `src/**/domain/**/*.py`
- `application-rules.md` — activates when editing `src/**/application/**/*.py`
- `infra-rules.md` — activates when editing `src/**/infrastructure/**/*.py`
