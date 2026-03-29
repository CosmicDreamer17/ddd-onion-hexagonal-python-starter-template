# DDD Onion Hexagonal Python Starter Template

A production-quality Python starter template implementing **Domain-Driven Design (DDD)**, **Onion Architecture**, and **Hexagonal Architecture (Ports and Adapters)**. Optimized for AI agent (Claude Code) maintenance with machine-verifiable architectural constraints.

## Architecture

```
                    ┌─────────────────────────────────┐
                    │        Infrastructure            │
                    │  (ORM, Repos, API, Adapters)     │
                    │                                  │
                    │    ┌───────────────────────┐     │
                    │    │      Application       │     │
                    │    │  (Use Cases, Queries)  │     │
                    │    │                        │     │
                    │    │    ┌──────────────┐    │     │
                    │    │    │    Domain     │    │     │
                    │    │    │  (Entities,   │    │     │
                    │    │    │   Ports)      │    │     │
                    │    │    └──────────────┘    │     │
                    │    └───────────────────────┘     │
                    └─────────────────────────────────┘

            Dependencies point INWARD only ->
```

### Bounded Contexts

- **work_management** -- Work items with lifecycle states (PENDING -> ACTIVE -> COMPLETED)
- **integration_management** -- External integration jobs (QUEUED -> PROCESSING -> DELIVERED/FAILED)

Contexts are fully isolated: no shared imports, no cross-context database foreign keys.

### Key Patterns

| Pattern | Location | Description |
|---------|----------|-------------|
| Entities | `src/*/domain/entities.py` | Pure Python dataclasses with invariant-enforcing methods |
| Ports | `src/*/domain/ports.py` | Abstract repository interfaces (`abc.ABC`) |
| Adapters | `src/*/infrastructure/repositories.py` | SQLAlchemy implementations with explicit ORM-to-domain mapping |
| Use Cases | `src/*/application/use_cases.py` | Transaction-scoped business operations (one function = one transaction) |
| Unit of Work | `src/shared/application/unit_of_work.py` | Abstract transaction boundary management |
| Read Models | `src/*/application/read_models.py` | Frozen dataclasses for query responses (CQRS read side) |
| Query Ports | `src/*/application/queries.py` | Abstract read-only query interfaces |
| Query Adapters | `src/*/infrastructure/query_adapters.py` | SQLAlchemy read-only query implementations |
| API Routers | `src/*/infrastructure/api.py` | FastAPI endpoints (HTTP adapter) |

## Quick Start

```bash
# Prerequisites: Python 3.12+ and uv
make install        # Install dependencies
make all-checks     # Run lint + tests + architecture checks + dependency checks
make serve          # Start FastAPI dev server at http://localhost:8000
```

## API Endpoints

### Work Items
```bash
# Create a work item
curl -X POST http://localhost:8000/work-items -H 'Content-Type: application/json' \
  -d '{"title": "My Task"}'

# List work items (optional ?status=pending|active|completed)
curl http://localhost:8000/work-items

# Get a specific work item
curl http://localhost:8000/work-items/{id}

# Assign, activate, complete
curl -X POST http://localhost:8000/work-items/{id}/assign \
  -H 'Content-Type: application/json' -d '{"owner_email": "alice@example.com"}'
curl -X POST http://localhost:8000/work-items/{id}/activate
curl -X POST http://localhost:8000/work-items/{id}/complete
```

### Integration Jobs
```bash
curl -X POST http://localhost:8000/integration-jobs \
  -H 'Content-Type: application/json' -d '{"source": "api", "payload": "data"}'
curl http://localhost:8000/integration-jobs
curl -X POST http://localhost:8000/integration-jobs/{id}/start
curl -X POST http://localhost:8000/integration-jobs/{id}/deliver
curl -X POST http://localhost:8000/integration-jobs/{id}/fail \
  -H 'Content-Type: application/json' -d '{"reason": "timeout"}'
curl -X POST http://localhost:8000/integration-jobs/{id}/retry
```

### System
```bash
curl http://localhost:8000/health      # Health check
curl http://localhost:8000/docs        # OpenAPI/Swagger UI
```

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

## Architecture Enforcement

Three automated mechanisms prevent architectural drift:

1. **import-linter** -- Static analysis enforcing onion layer direction and bounded context independence
2. **pytest-archon** -- Dynamic tests verifying domain purity (no SQLAlchemy in domain) and context isolation
3. **deptry** -- Dependency hygiene ensuring clean, accurate `pyproject.toml`

## Project Structure

```
src/
├── work_management/           # Bounded context: work items
│   ├── domain/                # Pure business logic (center of onion)
│   │   ├── entities.py        # WorkItem aggregate root
│   │   ├── value_objects.py   # WorkItemStatus enum
│   │   ├── exceptions.py      # Domain-specific errors
│   │   ├── ports.py           # WorkItemRepository interface
│   │   └── events.py          # WorkItemCompletedEvent (domain event)
│   ├── application/           # Use case orchestration + CQRS queries
│   │   ├── use_cases.py       # create, assign, activate, complete
│   │   ├── queries.py         # WorkItemQueryPort + query functions
│   │   └── read_models.py     # WorkItemReadModel (frozen dataclass)
│   └── infrastructure/        # External adapters
│       ├── orm.py             # SQLAlchemy WorkItemModel
│       ├── repositories.py    # SqlAlchemyWorkItemRepository
│       ├── query_adapters.py  # SqlAlchemyWorkItemQueryAdapter
│       ├── unit_of_work.py    # SqlAlchemyWorkManagementUnitOfWork
│       └── api.py             # FastAPI router
├── integration_management/    # Bounded context: external jobs
│   ├── domain/
│   ├── application/
│   └── infrastructure/
├── shared/                    # Cross-cutting concerns
│   ├── domain/
│   │   └── events.py          # DomainEvent base + EventBus protocol
│   ├── application/
│   │   └── unit_of_work.py    # AbstractUnitOfWork base
│   └── infrastructure/
│       ├── database.py        # SQLAlchemy engine and Base
│       ├── event_bus.py       # InMemoryEventBus adapter
│       └── app.py             # FastAPI application factory + event wiring
tests/
├── architecture/              # Architecture enforcement tests
├── work_management/           # Domain + use case + query + API tests
└── integration_management/    # Domain + use case + query + API tests
```

## Claude Code Integration

This template includes Claude Code configuration for AI-assisted development:

- **CLAUDE.md** -- Global architectural doctrine loaded every session
- **.claude/rules/** -- Path-scoped rules that activate only when touching specific layers
- **.claude/agents/** -- Specialized agent personas (planner, implementer, reviewer)

## Tech Stack

- **Python 3.12+**
- **FastAPI** (HTTP adapter)
- **SQLAlchemy 2.0** (infrastructure only)
- **SQLite** (default, swappable)
- **pytest** + **pytest-archon** (testing + architecture validation)
- **import-linter** (static dependency enforcement)
- **deptry** (dependency hygiene)
- **ruff** (linting + formatting)
- **uv** (package management)

## License

MIT
