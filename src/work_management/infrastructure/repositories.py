import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from work_management.domain.entities import WorkItem
from work_management.domain.ports import WorkItemRepository
from work_management.domain.value_objects import WorkItemStatus
from work_management.infrastructure.orm import WorkItemModel


class SqlAlchemyWorkItemRepository(WorkItemRepository):
    """Concrete adapter implementing WorkItemRepository using SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, item_id: uuid.UUID) -> WorkItem | None:
        model = self._session.get(WorkItemModel, str(item_id))
        if model is None:
            return None
        return self._to_domain(model)

    def save(self, work_item: WorkItem) -> None:
        model = self._to_model(work_item)
        self._session.merge(model)

    @staticmethod
    def _to_domain(model: WorkItemModel) -> WorkItem:
        return WorkItem(
            id=uuid.UUID(model.id),
            title=model.title,
            status=WorkItemStatus(model.status),
            version=model.version,
            assigned_to=model.assigned_to,
            created_at=datetime.fromisoformat(model.created_at),
            updated_at=datetime.fromisoformat(model.updated_at),
        )

    @staticmethod
    def _to_model(item: WorkItem) -> WorkItemModel:
        return WorkItemModel(
            id=str(item.id),
            title=item.title,
            status=item.status.value,
            assigned_to=item.assigned_to,
            version=item.version,
            created_at=item.created_at.isoformat(),
            updated_at=item.updated_at.isoformat(),
        )
