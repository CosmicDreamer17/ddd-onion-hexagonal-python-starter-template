import uuid

from integration_management.application.read_models import IntegrationJobReadModel
from integration_management.application.use_cases import IntegrationManagementUnitOfWork
from integration_management.domain.entities import IntegrationJob
from integration_management.domain.value_objects import JobStatus


def _to_read_model(job: IntegrationJob) -> IntegrationJobReadModel:
    return IntegrationJobReadModel(
        id=job.id,
        source=job.source,
        payload=job.payload,
        status=job.status.value,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def get_integration_job(
    uow: IntegrationManagementUnitOfWork, job_id: uuid.UUID
) -> IntegrationJobReadModel | None:
    """Fetch a single integration job by ID. Returns None if not found."""
    with uow:
        job = uow.jobs.get(job_id)
        if job is None:
            return None
        return _to_read_model(job)


def list_integration_jobs(
    uow: IntegrationManagementUnitOfWork,
    status_filter: JobStatus | None = None,
) -> list[IntegrationJobReadModel]:
    """List integration jobs, optionally filtered by status."""
    with uow:
        jobs = uow.jobs.list(status=status_filter)
        return [_to_read_model(job) for job in jobs]
