---
paths:
  - "src/**/application/**/*.py"
---

# Application Layer Rules

1. **NEVER** import from `*.infrastructure.*` modules.
2. May import from the same context's `domain` layer and from `shared.application`.
3. Use cases are plain functions, not classes. Each function accepts a UoW as its first parameter.
4. One use case function = one transaction. Pattern: `with uow:` -> domain logic -> `uow.commit()`.
5. Context-specific UoW ports extend `AbstractUnitOfWork` and expose repository ports as abstract properties.
6. Do not catch domain exceptions in use cases — let them propagate to the caller.
7. Do not import from other bounded contexts. If cross-context coordination is needed, use events.
8. Raise domain-specific "not found" errors (e.g., `WorkItemNotFoundError`), never generic `ValueError`.

# CQRS Query Rules

9. Read models in `read_models.py` are `@dataclass(frozen=True, slots=True)` — no mutation, no invariants.
10. Query ports in `queries.py` are `abc.ABC` classes with read-only methods (`get_by_id`, `list_by_status`).
11. Query functions accept a query port (not UoW). They never commit or modify data.
12. Read models use plain strings for status/timestamps (not enums/datetime). They are optimized for data transfer.
