import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from work_management.application.queries import WorkItemQueryPort
from work_management.application.read_models import WorkItemReadModel
from work_management.infrastructure.orm import WorkItemModel


class SqlAlchemyWorkItemQueryAdapter(WorkItemQueryPort):
    """Read-only query adapter for work items using SQLAlchemy."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def get_by_id(self, item_id: uuid.UUID) -> WorkItemReadModel | None:
        with Session(self._engine) as session:
            model = session.get(WorkItemModel, str(item_id))
            if model is None:
                return None
            return self._to_read_model(model)

    def list_by_status(self, status: str | None = None) -> list[WorkItemReadModel]:
        with Session(self._engine) as session:
            stmt = select(WorkItemModel)
            if status is not None:
                stmt = stmt.where(WorkItemModel.status == status)
            models = session.scalars(stmt).all()
            return [self._to_read_model(m) for m in models]

    @staticmethod
    def _to_read_model(model: WorkItemModel) -> WorkItemReadModel:
        return WorkItemReadModel(
            id=uuid.UUID(model.id),
            title=model.title,
            status=model.status,
            assigned_to=model.assigned_to,
            version=model.version,
            created_at=datetime.fromisoformat(model.created_at),
            updated_at=datetime.fromisoformat(model.updated_at),
        )
