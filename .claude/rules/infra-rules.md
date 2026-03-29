---
paths:
  - "src/**/infrastructure/**/*.py"
---

# Infrastructure Layer Rules

1. This is the only layer where SQLAlchemy and other frameworks may be imported.
2. ORM models live in `orm.py`. They extend `shared.infrastructure.database.Base`.
3. Repositories in `repositories.py` implement domain port interfaces from `domain/ports.py`.
4. Repositories **must** explicitly map between ORM models and domain entities using `_to_domain()` and `_to_model()` static methods.
5. ORM models must **never** leak into the application or domain layers.
6. Repositories must **never** call `commit()` or `rollback()` — that is the UoW's responsibility.
7. Use `session.merge()` for upsert semantics in `save()` methods.
8. Concrete UoW implementations create a `Session` in `__enter__` and close it in `__exit__`.
9. No cross-context foreign keys or shared tables between bounded contexts.
