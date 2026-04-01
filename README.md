# Python DDD & Hexagonal Starter Template

A production-ready Python starter template architected for **Domain-Driven Design (DDD)**, **Onion Architecture**, and **Hexagonal Architecture**. This repository is specifically optimized for **autonomous AI agents** (Claude, Gemini, Codex) and senior engineering teams.

## 🏛️ Core Architecture

The project follows a strict **Hexagonal (Ports and Adapters)** structure with an inward-pointing dependency flow:

*   **Domain Layer**: Pure business logic, entities, and repository ports. Zero external dependencies.
*   **Application Layer**: Use Cases (command orchestration), Read Models, and Query Ports.
*   **Infrastructure Layer**: Driven adapters (SQLAlchemy, external clients) that implement application ports.
*   **API Layer**: FastAPI routers and schemas.

## 🤖 AI-Native Optimization

This repository is designed to be maintained by AI agents with zero architectural drift:

*   **Master Agentic Protocol**: Centralized mandates in `AI.md` that govern all AI operations.
*   **Agent Wrappers**: Optimized entry points for [Claude](CLAUDE.md), [Gemini](GEMINI.md), and [Codex](CODEX.md).
*   **Architectural Enforcement**: 
    *   **import-linter**: Static analysis to prevent layer leakage.
    *   **pytest-archon**: Dynamic verification of domain purity.
    *   **deptry**: Dependency hygiene and accurate `pyproject.toml` management.

## 🚀 Quick Start

```bash
# Prerequisites: Python 3.12+ and uv
make install        # Sync dependencies
make verify         # Run full architectural and logic checks (Lint + Test + Arch)
make serve          # Start FastAPI dev server at http://localhost:8000
```

## 🛠️ Tech Stack

*   **Language**: Python 3.12+
*   **Framework**: FastAPI (API layer)
*   **ORM**: SQLAlchemy 2.0 (Infrastructure only)
*   **Tooling**: `uv` (Package management), `ruff` (Linting), `pytest` (Testing)
*   **Verification**: `import-linter`, `pytest-archon`, `deptry`

---
**Provenance**: Architected and implemented by **Gemini CLI** on March 29, 2026, for Howard Rhee.
