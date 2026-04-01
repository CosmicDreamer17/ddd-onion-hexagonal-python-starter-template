# Master Agentic Protocol: Python DDD & Hexagonal

This is the single source of truth for all AI agents (Claude, Gemini, Codex) maintaining this repository. This document defines the architectural mandates, operational protocols, and the non-negotiable verification standard.

## 1. Bootstrap Protocol
Before initiating any development cycle, ensure the environment is pristine:
1.  **Sync Environment**: `make install`
2.  **Verify Baseline**: `make verify`
3.  **Environment Check**: Ensure `.env` is configured correctly (refer to `.env.example`).

## 2. Architectural Mandates
This repository follows **Onion Architecture** and **Hexagonal Architecture (Ports and Adapters)**.

### Dependency Flow
*   **Inward Only**: `Infrastructure -> Application -> Domain`.
*   **Pure Domain**: The `domain` layer MUST remain free of frameworks (SQLAlchemy, FastAPI, etc.).
*   **Strict Isolation**: Bounded contexts (e.g., `work_management`, `integration_management`) MUST NEVER import from each other. Shared logic goes in `src/shared`.

### Layer Responsibilities
*   **Domain (`src/*/domain/`)**: Entities, Value Objects, Domain Exceptions, and Repository Ports (`abc.ABC`).
*   **Application (`src/*/application/`)**: Use Cases (orchestration), Query Ports, and Read Models.
*   **Infrastructure (`src/*/infrastructure/`)**: Repository Adapters (SQLAlchemy), Query Adapters, Unit of Work implementations, and API Routers (FastAPI).

## 3. The "Slice" Protocol (Development Order)
When implementing a new feature or context, follow the "Slice" order to ensure architectural integrity:
1.  **Domain**: Value Objects → Exceptions → Entities → Ports.
2.  **Application**: Use Cases → Read Models → Queries.
3.  **Infrastructure**: ORM Models → Repositories → Query Adapters → Unit of Work.
4.  **API**: FastAPI routers and schemas.
5.  **Tests**: Unit tests for Domain/Use Cases → Integration tests for API.

## 4. Operational Protocols

### Plan Mode First
For all complex changes (especially in Domain or Application layers), the agent MUST start with a `/plan` or a detailed strategy before modifying any code. 

### Verification is Finality
A task is NOT complete until `make verify` passes. This command runs:
*   **Linting**: Ruff (check + format).
*   **Tests**: Pytest.
*   **Architecture**: `import-linter` (layer and context isolation enforcement).
*   **Dependency Hygiene**: `deptry`.

## 5. Coding Patterns

*   **Entities**: Use `@dataclass(slots=True)` with a `create()` classmethod for instantiation. Enforce invariants in domain methods.
*   **Exceptions**: Use a `*Error` suffix (e.g., `ItemNotFoundError`). Extend the context's base error.
*   **UoW**: One Use Case = One Transaction. Use the `with uow:` pattern.
*   **Mapping**: Use explicit `_to_domain()` and `_to_model()` mapping in adapters. NEVER leak ORM models into Domain/Application.

---
**Provenance**: Architected for Howard Rhee on March 29, 2026. Optimized for AI-native autonomous maintenance.
