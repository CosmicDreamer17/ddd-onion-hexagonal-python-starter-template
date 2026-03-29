import abc
import uuid

from integration_management.domain.entities import IntegrationJob
from integration_management.domain.ports import IntegrationJobRepository
from shared.application.unit_of_work import AbstractUnitOfWork


class IntegrationManagementUnitOfWork(AbstractUnitOfWork):
    """Port defining the unit of work for the integration management bounded context."""

    @property
    @abc.abstractmethod
    def jobs(self) -> IntegrationJobRepository: ...


def create_integration_job(
    uow: IntegrationManagementUnitOfWork, source: str, payload: str
) -> uuid.UUID:
    """Create a new integration job in QUEUED status."""
    with uow:
        job = IntegrationJob.create(source, payload)
        uow.jobs.save(job)
        uow.commit()
        return job.id


def start_processing_job(
    uow: IntegrationManagementUnitOfWork, job_id: uuid.UUID
) -> None:
    """Start processing a queued integration job."""
    with uow:
        job = uow.jobs.get(job_id)
        if job is None:
            raise ValueError(f"IntegrationJob {job_id} not found.")
        job.start_processing()
        uow.jobs.save(job)
        uow.commit()


def deliver_job(uow: IntegrationManagementUnitOfWork, job_id: uuid.UUID) -> None:
    """Mark a processing job as delivered."""
    with uow:
        job = uow.jobs.get(job_id)
        if job is None:
            raise ValueError(f"IntegrationJob {job_id} not found.")
        job.mark_delivered()
        uow.jobs.save(job)
        uow.commit()


def fail_job(
    uow: IntegrationManagementUnitOfWork, job_id: uuid.UUID, reason: str
) -> None:
    """Mark a processing job as failed."""
    with uow:
        job = uow.jobs.get(job_id)
        if job is None:
            raise ValueError(f"IntegrationJob {job_id} not found.")
        job.mark_failed(reason)
        uow.jobs.save(job)
        uow.commit()


def retry_job(uow: IntegrationManagementUnitOfWork, job_id: uuid.UUID) -> None:
    """Retry a failed integration job by re-queuing it."""
    with uow:
        job = uow.jobs.get(job_id)
        if job is None:
            raise ValueError(f"IntegrationJob {job_id} not found.")
        job.retry()
        uow.jobs.save(job)
        uow.commit()
