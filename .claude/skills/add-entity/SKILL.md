---
name: add-entity
description: Add a new entity to an existing bounded context following DDD patterns
disable-model-invocation: true
---

Add a new entity to a bounded context: $ARGUMENTS

Parse the arguments to determine the context name and entity name. Then follow these steps in order:

1. **Domain value objects** (`src/{context}/domain/value_objects.py`):
   - Add any new enums needed for the entity's state or types

2. **Domain exceptions** (`src/{context}/domain/exceptions.py`):
   - Add `{Entity}NotFoundError` extending the context base error
   - Add any state transition errors needed

3. **Domain entity** (`src/{context}/domain/entities.py` or new file):
   ```python
   @dataclass(slots=True)
   class {Entity}:
       id: uuid.UUID
       # ... fields

       @classmethod
       def create(cls, ...) -> "{Entity}":
           return cls(id=uuid.uuid4(), ...)
   ```

4. **Domain port** (`src/{context}/domain/ports.py`):
   ```python
   class {Entity}Repository(abc.ABC):
       @abc.abstractmethod
       def get(self, id: uuid.UUID) -> {Entity} | None: ...
       @abc.abstractmethod
       def save(self, entity: {Entity}) -> None: ...
   ```

5. **Application use cases** (`src/{context}/application/use_cases.py`):
   - Add the repository as an abstract property on the context's UoW
   - Add use case functions (create, update, etc.)

6. **Application read model** (`src/{context}/application/read_models.py`):
   - Add `@dataclass(frozen=True, slots=True)` read model

7. **Application queries** (`src/{context}/application/queries.py`):
   - Add query port and query functions

8. **Infrastructure ORM** (`src/{context}/infrastructure/orm.py`):
   - Add SQLAlchemy model extending `Base`

9. **Infrastructure repository** (`src/{context}/infrastructure/repositories.py`):
   - Add `SqlAlchemy{Entity}Repository` with explicit `_to_domain()` and `_to_model()`

10. **Infrastructure query adapter** (`src/{context}/infrastructure/query_adapters.py`)

11. **Infrastructure UoW** — update to include new repository

12. **API endpoints** (`src/{context}/infrastructure/api.py`):
    - Add Pydantic schemas and route handlers

13. **Tests**: domain, use cases, queries, API

14. **Verify**: Run `make all-checks`
