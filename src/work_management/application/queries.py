import uuid

from work_management.application.read_models import WorkItemReadModel
from work_management.application.use_cases import WorkManagementUnitOfWork
from work_management.domain.entities import WorkItem
from work_management.domain.value_objects import WorkItemStatus


def _to_read_model(item: WorkItem) -> WorkItemReadModel:
    return WorkItemReadModel(
        id=item.id,
        title=item.title,
        status=item.status.value,
        assigned_to=item.assigned_to,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def get_work_item(
    uow: WorkManagementUnitOfWork, item_id: uuid.UUID
) -> WorkItemReadModel | None:
    """Fetch a single work item by ID. Returns None if not found."""
    with uow:
        item = uow.work_items.get(item_id)
        if item is None:
            return None
        return _to_read_model(item)


def list_work_items(
    uow: WorkManagementUnitOfWork,
    status_filter: WorkItemStatus | None = None,
) -> list[WorkItemReadModel]:
    """List work items, optionally filtered by status."""
    with uow:
        items = uow.work_items.list(status=status_filter)
        return [_to_read_model(item) for item in items]
