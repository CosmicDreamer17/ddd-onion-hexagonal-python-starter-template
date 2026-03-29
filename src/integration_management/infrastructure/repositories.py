import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from integration_management.domain.entities import IntegrationJob
from integration_management.domain.ports import IntegrationJobRepository
from integration_management.domain.value_objects import JobStatus
from integration_management.infrastructure.orm import IntegrationJobModel


class SqlAlchemyIntegrationJobRepository(IntegrationJobRepository):
    """Concrete adapter implementing IntegrationJobRepository using SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, job_id: uuid.UUID) -> IntegrationJob | None:
        model = self._session.get(IntegrationJobModel, str(job_id))
        if model is None:
            return None
        return self._to_domain(model)

    def save(self, job: IntegrationJob) -> None:
        model = self._to_model(job)
        self._session.merge(model)

    @staticmethod
    def _to_domain(model: IntegrationJobModel) -> IntegrationJob:
        return IntegrationJob(
            id=uuid.UUID(model.id),
            source=model.source,
            payload=model.payload,
            status=JobStatus(model.status),
            error_message=model.error_message,
            created_at=datetime.fromisoformat(model.created_at),
            updated_at=datetime.fromisoformat(model.updated_at),
        )

    @staticmethod
    def _to_model(job: IntegrationJob) -> IntegrationJobModel:
        return IntegrationJobModel(
            id=str(job.id),
            source=job.source,
            payload=job.payload,
            status=job.status.value,
            error_message=job.error_message,
            created_at=job.created_at.isoformat(),
            updated_at=job.updated_at.isoformat(),
        )
