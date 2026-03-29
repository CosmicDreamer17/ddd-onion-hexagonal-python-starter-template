# DDD Onion Hexagonal Python Starter Template

A production-quality Python starter template implementing **Domain-Driven Design (DDD)**, **Onion Architecture**, and **Hexagonal Architecture (Ports and Adapters)**. Optimized for AI agent (Claude Code) maintenance with machine-verifiable architectural constraints.

## Architecture

```
                    ┌─────────────────────────────────┐
                    │        Infrastructure            │
                    │  (ORM, Repositories, Adapters)   │
                    │                                  │
                    │    ┌───────────────────────┐     │
                    │    │      Application       │     │
                    │    │   (Use Cases, UoW)     │     │
                    │    │                        │     │
                    │    │    ┌──────────────┐    │     │
                    │    │    │    Domain     │    │     │
                    │    │    │  (Entities,   │    │     │
                    │    │    │   Ports)      │    │     │
                    │    │    └──────────────┘    │     │
                    │    └───────────────────────┘     │
                    └─────────────────────────────────┘

            Dependencies point INWARD only →
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

## Quick Start

```bash
# Prerequisites: Python 3.12+ and uv
make install        # Install dependencies
make all-checks     # Run lint + tests + architecture checks + dependency checks
```

## Development Commands

```bash
make install        # Install dependencies with uv
make test           # Run pytest (44 tests)
make lint           # Run ruff check + format check
make format         # Auto-format with ruff
make arch-check     # Run import-linter (static layer enforcement)
make deps-check     # Run deptry (dependency hygiene)
make all-checks     # Run all of the above
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
│   │   └── ports.py           # WorkItemRepository interface
│   ├── application/           # Use case orchestration
│   │   └── use_cases.py       # create, assign, activate, complete
│   └── infrastructure/        # External adapters
│       ├── orm.py             # SQLAlchemy WorkItemModel
│       ├── repositories.py    # SqlAlchemyWorkItemRepository
│       └── unit_of_work.py    # SqlAlchemyWorkManagementUnitOfWork
├── integration_management/    # Bounded context: external jobs
│   ├── domain/
│   ├── application/
│   └── infrastructure/
├── shared/                    # Cross-cutting concerns
│   ├── application/
│   │   └── unit_of_work.py    # AbstractUnitOfWork base
│   └── infrastructure/
│       └── database.py        # SQLAlchemy engine and Base
tests/
├── architecture/              # Architecture enforcement tests
├── work_management/           # Domain + use case tests
└── integration_management/    # Domain + use case tests
```

## Claude Code Integration

This template includes Claude Code configuration for AI-assisted development:

- **CLAUDE.md** -- Global architectural doctrine loaded every session
- **.claude/rules/** -- Path-scoped rules that activate only when touching specific layers
- **.claude/agents/** -- Specialized agent personas (planner, implementer, reviewer)

## Tech Stack

- **Python 3.12+**
- **SQLAlchemy 2.0** (infrastructure only)
- **SQLite** (default, swappable)
- **pytest** + **pytest-archon** (testing + architecture validation)
- **import-linter** (static dependency enforcement)
- **deptry** (dependency hygiene)
- **ruff** (linting + formatting)
- **uv** (package management)
