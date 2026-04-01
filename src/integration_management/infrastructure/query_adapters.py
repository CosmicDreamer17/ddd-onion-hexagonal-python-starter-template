import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from integration_management.application.queries import IntegrationJobQueryPort
from integration_management.application.read_models import IntegrationJobReadModel
from integration_management.infrastructure.orm import IntegrationJobModel


class SqlAlchemyIntegrationJobQueryAdapter(IntegrationJobQueryPort):
    """Read-only query adapter for integration jobs using SQLAlchemy."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def get_by_id(self, job_id: uuid.UUID) -> IntegrationJobReadModel | None:
        with Session(self._engine) as session:
            model = session.get(IntegrationJobModel, str(job_id))
            if model is None:
                return None
            return self._to_read_model(model)

    def list_by_status(
        self, status: str | None = None
    ) -> list[IntegrationJobReadModel]:
        with Session(self._engine) as session:
            stmt = select(IntegrationJobModel)
            if status is not None:
                stmt = stmt.where(IntegrationJobModel.status == status)
            models = session.scalars(stmt).all()
            return [self._to_read_model(m) for m in models]

    @staticmethod
    def _to_read_model(model: IntegrationJobModel) -> IntegrationJobReadModel:
        return IntegrationJobReadModel(
            id=uuid.UUID(model.id),
            source=model.source,
            payload=model.payload,
            status=model.status,
            error_message=model.error_message,
            created_at=datetime.fromisoformat(model.created_at),
            updated_at=datetime.fromisoformat(model.updated_at),
        )
