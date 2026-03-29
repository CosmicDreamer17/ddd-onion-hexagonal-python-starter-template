# Contributing Guide

This guide explains how to extend the template while maintaining architectural integrity. Whether you are a developer or an AI agent, follow these steps precisely.

---

## Architecture Overview

This project implements three complementary patterns:

- **Domain-Driven Design (DDD)**: Business logic lives in domain entities with explicit invariants.
- **Onion Architecture**: Dependencies point strictly inward — infrastructure → application → domain.
- **Hexagonal Architecture (Ports and Adapters)**: The domain defines abstract ports; infrastructure provides concrete adapters.

### Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     INFRASTRUCTURE                          │
│  (SQLAlchemy ORM, concrete repositories, concrete UoW)      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   APPLICATION                         │  │
│  │  (use case functions, UoW port, orchestration)        │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │                  DOMAIN                         │  │  │
│  │  │  (entities, value objects, exceptions, ports)   │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Key rule**: imports flow inward only. The domain layer never imports from application or infrastructure. The application layer never imports from infrastructure.

### Bounded Context Diagram

```
┌──────────────────────────┐    ┌──────────────────────────────┐
│    work_management       │    │   integration_management     │
│  ┌────────────────────┐  │    │  ┌──────────────────────┐   │
│  │  domain            │  │    │  │  domain              │   │
│  │  application       │  │    │  │  application         │   │
│  │  infrastructure    │  │    │  │  infrastructure      │   │
│  └────────────────────┘  │    │  └──────────────────────┘   │
└──────────────────────────┘    └──────────────────────────────┘
           │                                  │
           └──────────────┬───────────────────┘
                          │  NO cross-imports allowed
                    ┌─────▼─────┐
                    │  shared   │
                    │ (UoW base,│
                    │ DB base)  │
                    └───────────┘
```

Bounded contexts are completely isolated. They must never import from each other. Cross-context coordination requires events or an anti-corruption layer.

---

## Development Setup

```bash
make install        # Install dependencies with uv
make test           # Run pytest
make lint           # Run ruff check + format check
make format         # Auto-format with ruff
make arch-check     # Run import-linter (static layer enforcement)
make deps-check     # Run deptry (dependency hygiene)
make all-checks     # Run all checks (required before declaring any task done)
```

Always run `make all-checks` before declaring a task complete.

---

## Guide: Adding a New Bounded Context

Use this when you need to model a completely new domain area (e.g., `billing_management`, `notification_management`).

### Step 1 — Create the directory structure

```
src/<context_name>/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── value_objects.py
│   ├── exceptions.py
│   ├── entities.py
│   └── ports.py
├── application/
│   ├── __init__.py
│   └── use_cases.py
└── infrastructure/
    ├── __init__.py
    ├── orm.py
    ├── repositories.py
    └── unit_of_work.py
```

### Step 2 — Add value objects (`domain/value_objects.py`)

Define enums for status fields and any other typed value objects:

```python
import enum

class MyEntityStatus(enum.StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    CLOSED = "closed"
```

### Step 3 — Add exceptions (`domain/exceptions.py`)

All exceptions must extend a context-specific base error and use the `Error` suffix:

```python
class MyContextError(Exception):
    """Base error for the my_context bounded context."""

class InvalidStateTransitionError(MyContextError):
    def __init__(self, from_status: str, to_status: str) -> None:
        super().__init__(f"Cannot transition from {from_status!r} to {to_status!r}.")
```

### Step 4 — Add entities (`domain/entities.py`)

Entities use `@dataclass(slots=True)` with a `create()` classmethod factory. State transitions are domain methods that raise domain exceptions. Only Python stdlib imports are allowed.

```python
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from my_context.domain.exceptions import InvalidStateTransitionError
from my_context.domain.value_objects import MyEntityStatus


@dataclass(slots=True)
class MyEntity:
    id: uuid.UUID
    name: str
    status: MyEntityStatus
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, name: str) -> "MyEntity":
        now = datetime.now(UTC)
        return cls(
            id=uuid.uuid4(),
            name=name,
            status=MyEntityStatus.PENDING,
            version=1,
            created_at=now,
            updated_at=now,
        )

    def activate(self) -> None:
        if self.status != MyEntityStatus.PENDING:
            raise InvalidStateTransitionError(self.status.value, MyEntityStatus.ACTIVE.value)
        self.status = MyEntityStatus.ACTIVE
        self.updated_at = datetime.now(UTC)
        self.version += 1
```

See `src/work_management/domain/entities.py` for the canonical example.

### Step 5 — Add repository port (`domain/ports.py`)

Define the abstract repository interface in the domain layer using `abc.ABC`:

```python
import abc
import uuid

from my_context.domain.entities import MyEntity


class MyEntityRepository(abc.ABC):
    @abc.abstractmethod
    def get(self, entity_id: uuid.UUID) -> MyEntity | None: ...

    @abc.abstractmethod
    def save(self, entity: MyEntity) -> None: ...
```

### Step 6 — Add use cases and UoW port (`application/use_cases.py`)

Define the context-specific UoW port first, then plain-function use cases. Each use case = one transaction.

```python
import abc
import uuid

from shared.application.unit_of_work import AbstractUnitOfWork
from my_context.domain.entities import MyEntity
from my_context.domain.ports import MyEntityRepository


class MyContextUnitOfWork(AbstractUnitOfWork):
    @property
    @abc.abstractmethod
    def my_entities(self) -> MyEntityRepository: ...


def create_my_entity(uow: MyContextUnitOfWork, name: str) -> uuid.UUID:
    with uow:
        entity = MyEntity.create(name)
        uow.my_entities.save(entity)
        uow.commit()
        return entity.id


def activate_my_entity(uow: MyContextUnitOfWork, entity_id: uuid.UUID) -> None:
    with uow:
        entity = uow.my_entities.get(entity_id)
        if entity is None:
            raise ValueError(f"MyEntity {entity_id} not found.")
        entity.activate()
        uow.my_entities.save(entity)
        uow.commit()
```

See `src/work_management/application/use_cases.py` for the canonical example.

### Step 7 — Add ORM model (`infrastructure/orm.py`)

ORM models extend `shared.infrastructure.database.Base`. Store all fields as primitive types (strings, ints); no domain objects leak into the ORM layer.

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from shared.infrastructure.database import Base


class MyEntityModel(Base):
    __tablename__ = "my_entities"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    version: Mapped[int]
    created_at: Mapped[str] = mapped_column(String, nullable=False)
    updated_at: Mapped[str] = mapped_column(String, nullable=False)
```

### Step 8 — Add repository adapter (`infrastructure/repositories.py`)

Implement the domain port with explicit `_to_domain()` and `_to_model()` static methods. Never call `commit()` or `rollback()` in a repository.

```python
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from my_context.domain.entities import MyEntity
from my_context.domain.ports import MyEntityRepository
from my_context.domain.value_objects import MyEntityStatus
from my_context.infrastructure.orm import MyEntityModel


class SqlAlchemyMyEntityRepository(MyEntityRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, entity_id: uuid.UUID) -> MyEntity | None:
        model = self._session.get(MyEntityModel, str(entity_id))
        if model is None:
            return None
        return self._to_domain(model)

    def save(self, entity: MyEntity) -> None:
        self._session.merge(self._to_model(entity))

    @staticmethod
    def _to_domain(model: MyEntityModel) -> MyEntity:
        return MyEntity(
            id=uuid.UUID(model.id),
            name=model.name,
            status=MyEntityStatus(model.status),
            version=model.version,
            created_at=datetime.fromisoformat(model.created_at),
            updated_at=datetime.fromisoformat(model.updated_at),
        )

    @staticmethod
    def _to_model(entity: MyEntity) -> MyEntityModel:
        return MyEntityModel(
            id=str(entity.id),
            name=entity.name,
            status=entity.status.value,
            version=entity.version,
            created_at=entity.created_at.isoformat(),
            updated_at=entity.updated_at.isoformat(),
        )
```

See `src/work_management/infrastructure/repositories.py` for the canonical example.

### Step 9 — Add concrete UoW (`infrastructure/unit_of_work.py`)

```python
from sqlalchemy.orm import Session, sessionmaker

from my_context.application.use_cases import MyContextUnitOfWork
from my_context.infrastructure.repositories import SqlAlchemyMyEntityRepository


class SqlAlchemyMyContextUnitOfWork(MyContextUnitOfWork):
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    def __enter__(self) -> "SqlAlchemyMyContextUnitOfWork":
        self._session: Session = self._session_factory()
        self._my_entities = SqlAlchemyMyEntityRepository(self._session)
        return super().__enter__()

    def __exit__(self, *args) -> None:
        super().__exit__(*args)
        self._session.close()

    @property
    def my_entities(self) -> SqlAlchemyMyEntityRepository:
        return self._my_entities

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
```

### Step 10 — Register the context in enforcement configuration

**`.importlinter`** — Add a layers contract for your new context:

```ini
[importlinter:contract:my-context-layers]
name = Onion layer enforcement for my_context
type = layers
layers =
    my_context.infrastructure
    my_context.application
    my_context.domain
```

Also add `my_context` to the `bounded-context-independence` contract's `modules` list.

**`pyproject.toml`** — Add `my_context` to `[tool.deptry] known_first_party`:

```toml
[tool.deptry]
known_first_party = ["work_management", "integration_management", "my_context", "shared"]
```

### Step 11 — Add tests

Follow the structure of existing test modules:

```
tests/<context_name>/
├── __init__.py
├── test_domain.py      # Entity invariant tests
└── test_use_cases.py   # Use case integration tests with in-memory SQLite
```

Add a fixture to `tests/conftest.py`:

```python
@pytest.fixture
def my_context_uow(engine):
    return SqlAlchemyMyContextUnitOfWork(create_session_factory(engine))
```

Update `create_tables` to include your new ORM model (it picks up all models that extend `Base` automatically once imported in `conftest.py`).

Add architecture tests to `tests/architecture/test_architecture.py` if needed — check that the existing pytest-archon rules already cover your new context paths.

### Step 12 — Verify

```bash
make all-checks
```

All checks must pass before the task is complete.

---

## Guide: Adding a New Entity to an Existing Context

Use this when you need to add a second aggregate root to an existing bounded context (e.g., adding `WorkQueue` to `work_management`).

Follow the same file-by-file order: **value objects → exceptions → entity → port → use cases → ORM → repository → UoW update → tests**.

**Key differences from a new context:**

1. **Exceptions** extend the existing context base error (`WorkManagementError`, `IntegrationManagementError`), not a new one.
2. **UoW port** gets a new abstract property for the new repository (extend `WorkManagementUnitOfWork`, do not replace it).
3. **Concrete UoW** adds the new repository instantiation in `__enter__` and the new property.
4. **`.importlinter`** requires no changes — the existing layers contract already covers all modules within the context.
5. **`pyproject.toml`** requires no changes — the context is already registered.

Example: Adding `WorkQueue` to `work_management`:

- `src/work_management/domain/value_objects.py` — add `QueueStatus`
- `src/work_management/domain/exceptions.py` — add `QueueCapacityExceededError(WorkManagementError)`
- `src/work_management/domain/entities.py` — add `WorkQueue` dataclass
- `src/work_management/domain/ports.py` — add `WorkQueueRepository(abc.ABC)`
- `src/work_management/application/use_cases.py` — add `work_queues` property to `WorkManagementUnitOfWork`, add new use case functions
- `src/work_management/infrastructure/orm.py` — add `WorkQueueModel`
- `src/work_management/infrastructure/repositories.py` — add `SqlAlchemyWorkQueueRepository`
- `src/work_management/infrastructure/unit_of_work.py` — add `work_queues` property and instantiation
- `tests/work_management/test_domain.py` — add `WorkQueue` invariant tests
- `tests/work_management/test_use_cases.py` — add use case integration tests

---

## Guide: Adding a New Infrastructure Adapter

Use this when you want to swap or add an alternative implementation for an existing repository port (e.g., an in-memory adapter for testing, a Redis-backed adapter, or a REST client adapter).

### Requirements

- The adapter must implement the domain port exactly (same method signatures).
- The adapter lives in the infrastructure layer only.
- It must never import from or expose domain internals beyond what the port defines.
- Naming convention: prefix with the technology name (e.g., `InMemoryWorkItemRepository`, `RedisWorkItemRepository`).

### Example: In-Memory Adapter

```python
import uuid
from my_context.domain.entities import MyEntity
from my_context.domain.ports import MyEntityRepository


class InMemoryMyEntityRepository(MyEntityRepository):
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, MyEntity] = {}

    def get(self, entity_id: uuid.UUID) -> MyEntity | None:
        return self._store.get(entity_id)

    def save(self, entity: MyEntity) -> None:
        self._store[entity.id] = entity
```

To use this in tests, create a matching in-memory UoW:

```python
from shared.application.unit_of_work import AbstractUnitOfWork
from my_context.application.use_cases import MyContextUnitOfWork


class InMemoryMyContextUnitOfWork(MyContextUnitOfWork):
    def __init__(self) -> None:
        self._my_entities = InMemoryMyEntityRepository()
        self.committed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    @property
    def my_entities(self):
        return self._my_entities

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass
```

### No Changes Required

Adding a new adapter requires no changes to `.importlinter`, `pyproject.toml`, or the domain/application layers. The architecture enforcement tools will verify the adapter only imports inward.

---

## Enforcement Tooling

Three automated mechanisms enforce architectural rules on every change.

### 1. import-linter (`.importlinter`)

**What it checks**: Static import graph. Verifies that dependencies only flow inward (infrastructure → application → domain) and that bounded contexts never import from each other.

**How to run**:

```bash
make arch-check
# equivalent to: uv run lint-imports
```

**When it fails**: You have an import that violates layer direction or crosses a context boundary. Read the error output — it names the exact import chain. Fix the import by introducing a proper port/adapter or by moving code to the correct layer.

**Configuration**: `.importlinter` at the project root. Add a new `layers` contract when adding a new bounded context.

### 2. pytest-archon (`tests/architecture/test_architecture.py`)

**What it checks**: Dynamic architecture rules enforced as pytest tests. Verifies:
- Domain layers contain no SQLAlchemy imports
- Application layers contain no infrastructure imports
- Bounded contexts do not cross-import

**How to run**:

```bash
make test
# architecture tests are included in the full test suite
```

**When it fails**: A specific module has an import it should not have. The test output names the offending module. Fix by removing the import and using a proper abstraction.

**Configuration**: `tests/architecture/test_architecture.py`. Extend this file when adding new contexts or rules.

### 3. deptry (`pyproject.toml`)

**What it checks**: Dependency hygiene. Catches missing dependencies (used but not declared), unused dependencies (declared but not used), and transitive dependency leaks (using a package without directly depending on it).

**How to run**:

```bash
make deps-check
# equivalent to: uv run deptry src/
```

**When it fails**: Update `pyproject.toml` — add a missing dependency or remove an unused one. When adding a new first-party package (new context), add it to `[tool.deptry] known_first_party`.

**Configuration**: `[tool.deptry]` section in `pyproject.toml`.

### 4. ruff

**What it checks**: Linting (style, correctness, imports) and formatting.

**How to run**:

```bash
make lint      # check only
make format    # auto-fix formatting
```

---

## Claude Code Agent Workflow

This repository ships with three specialized Claude Code agents in `.claude/agents/`. They are designed to work in sequence for safe, architecture-compliant development.

### Agent Roles

#### Planner (`.claude/agents/planner.yaml`)

- **Role**: Read-only architecture analysis. Maps requirements to the correct bounded context and layers.
- **Output**: A step-by-step implementation plan with exact file paths and the correct order of changes.
- **Does not modify files.**
- **Invoke when**: Starting any non-trivial feature. Ask the Planner to produce a plan before writing any code.

#### Implementer (`.claude/agents/implementer.yaml`)

- **Role**: Code generation following the exact patterns in this repository.
- **Input**: The Planner's step-by-step plan.
- **Output**: Working code across all layers, in the correct order.
- **Runs `make all-checks` after implementation** and fixes any failures before finishing.

#### Reviewer (`.claude/agents/reviewer.yaml`)

- **Role**: Architecture validation audit. Runs enforcement tools and checks for violations.
- **Review checklist**:
  1. Domain purity: no framework imports in `src/*/domain/`
  2. Layer direction: infrastructure → application → domain only
  3. Context isolation: no cross-context imports
  4. Repository mapping: explicit `_to_domain()` and `_to_model()` in all repositories
  5. UoW pattern: one use case = one transaction, repositories never call `commit()`
  6. Naming conventions: `Error` suffix on exceptions, `SqlAlchemy` prefix on adapters
  7. All enforcement tools pass: pytest, import-linter, deptry, ruff

### Recommended Workflow

```
1. Planner  → Analyze and produce implementation plan
2. Implementer → Execute plan, run make all-checks
3. Reviewer → Audit changes, confirm all checks pass
```

### Path-Scoped Rules

Automatic rules activate when editing specific paths:

| Path | Rule file | Enforces |
|------|-----------|----------|
| `src/*/domain/` | `.claude/rules/domain-rules.md` | Pure Python stdlib only, no framework imports |
| `src/*/application/` | `.claude/rules/application-rules.md` | No infrastructure imports, one UoW per use case |
| `src/*/infrastructure/` | `.claude/rules/infra-rules.md` | Explicit mapping, no ORM leakage, session lifecycle |

These rules are loaded automatically by Claude Code when files in those paths are opened or edited.

---

## Quick Reference

### File Creation Order

When adding a new entity or context, always follow this order:

```
value_objects.py → exceptions.py → entities.py → ports.py →
use_cases.py → orm.py → repositories.py → unit_of_work.py → tests
```

This order ensures each file only depends on files that already exist.

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Domain exception | `Error` suffix | `InvalidStateTransitionError` |
| Repository adapter | `SqlAlchemy` prefix | `SqlAlchemyWorkItemRepository` |
| Concrete UoW | `SqlAlchemy` prefix | `SqlAlchemyWorkManagementUnitOfWork` |
| ORM model | `Model` suffix | `WorkItemModel` |
| Context base error | Context name + `Error` | `WorkManagementError` |

### What Goes Where

| Artifact | Layer | File |
|----------|-------|------|
| Enums, typed values | Domain | `domain/value_objects.py` |
| Domain exceptions | Domain | `domain/exceptions.py` |
| Aggregate roots | Domain | `domain/entities.py` |
| Repository interfaces (ports) | Domain | `domain/ports.py` |
| Use cases, UoW port | Application | `application/use_cases.py` |
| ORM models | Infrastructure | `infrastructure/orm.py` |
| Repository adapters | Infrastructure | `infrastructure/repositories.py` |
| Concrete UoW | Infrastructure | `infrastructure/unit_of_work.py` |

### Allowed Imports by Layer

| Layer | May import from |
|-------|----------------|
| Domain | Python stdlib only (`uuid`, `dataclasses`, `enum`, `abc`, `typing`, `datetime`) |
| Application | Domain layer, `shared.application` |
| Infrastructure | Application layer, Domain layer, `shared`, SQLAlchemy and other frameworks |
