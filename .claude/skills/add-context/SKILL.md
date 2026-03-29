---
name: add-context
description: Add a new bounded context to the project following DDD/Onion/Hexagonal patterns
disable-model-invocation: true
---

Add a new bounded context: $ARGUMENTS

Parse the arguments to determine the context name. Then follow these steps:

1. **Create directory structure**:
   ```
   src/{context}/
   ├── __init__.py
   ├── py.typed
   ├── domain/
   │   ├── __init__.py
   │   ├── value_objects.py
   │   ├── exceptions.py
   │   ├── entities.py
   │   └── ports.py
   ├── application/
   │   ├── __init__.py
   │   ├── use_cases.py
   │   ├── read_models.py
   │   └── queries.py
   └── infrastructure/
       ├── __init__.py
       ├── orm.py
       ├── repositories.py
       ├── query_adapters.py
       ├── unit_of_work.py
       └── api.py
   ```

2. **Register in pyproject.toml**: Add `"src/{context}"` to `[tool.hatch.build.targets.wheel] packages`

3. **Register in .importlinter**: Add layers contract and update independence contract

4. **Add architecture tests** in `tests/architecture/test_architecture.py`

5. **Wire into app factory** (`src/shared/infrastructure/app.py`)

6. **Create test directory** `tests/{context}/` with domain, use case, query, and API tests

7. **Import ORM models** in conftest.py engine fixture and in app factory

8. **Verify**: Run `make all-checks` — all contracts must pass

Reference existing contexts (`work_management`, `integration_management`) for exact patterns to follow.
