"""Example entrypoint demonstrating the full work item lifecycle.

Runs the four work management use cases end-to-end:
  create → assign owner → activate → complete
"""

import os

# Import ORM models before create_tables so SQLAlchemy registers them.
import work_management.infrastructure.orm  # noqa: F401
from shared.infrastructure.database import create_engine, create_tables
from work_management.application.use_cases import (
    activate_work_item,
    assign_work_item,
    complete_work_item,
    create_work_item,
)
from work_management.infrastructure.unit_of_work import (
    SqlAlchemyWorkManagementUnitOfWork,
)


def main() -> None:
    database_url = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    engine = create_engine(database_url)
    create_tables(engine)

    uow = SqlAlchemyWorkManagementUnitOfWork(engine)

    print("=== DDD Onion Hexagonal — Work Item Lifecycle Demo ===\n")

    item_id = create_work_item(uow, title="Implement Docker support")
    print(f"[1] Created work item  id={item_id}")

    assign_work_item(uow, item_id, owner_email="dev@example.com")
    print(f"[2] Assigned owner     id={item_id}  owner=dev@example.com")

    activate_work_item(uow, item_id)
    print(f"[3] Activated          id={item_id}")

    complete_work_item(uow, item_id)
    print(f"[4] Completed          id={item_id}")

    print("\nLifecycle complete. All use cases executed successfully.")


if __name__ == "__main__":
    main()
