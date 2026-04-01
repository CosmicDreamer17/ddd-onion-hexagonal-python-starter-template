---
paths:
  - "src/**/domain/**/*.py"
---

# Domain Layer Rules

1. **ONLY** use Python stdlib imports: `dataclasses`, `uuid`, `enum`, `abc`, `typing`, `datetime`.
2. **NEVER** import `sqlalchemy`, `fastapi`, `flask`, or any framework library.
3. **NEVER** import from `*.infrastructure.*` or `*.application.*` modules.
4. Entities use `@dataclass(slots=True)` with a `create()` classmethod factory.
5. State transitions are enforced in domain methods that raise domain-specific exceptions.
6. Exception classes extend the context's base error and use the `Error` suffix (e.g., `InvalidStateTransitionError`).
7. Repository ports are `abc.ABC` classes with `@abstractmethod` decorators.
8. Domain objects must be fully self-contained — no lazy loading, no session tracking.
