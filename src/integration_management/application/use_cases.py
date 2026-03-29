import abc
import logging
import uuid

from integration_management.domain.entities import IntegrationJob
from integration_management.domain.exceptions import IntegrationJobNotFoundError
from integration_management.domain.ports import IntegrationJobRepository
from shared.application.unit_of_work import AbstractUnitOfWork

logger = logging.getLogger(__name__)


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
        logger.info("Created integration job %s from %s", job.id, source)
        return job.id


def start_processing_job(
    uow: IntegrationManagementUnitOfWork, job_id: uuid.UUID
) -> None:
    """Start processing a queued integration job."""
    with uow:
        job = uow.jobs.get(job_id)
        if job is None:
            raise IntegrationJobNotFoundError(job_id)
        job.start_processing()
        uow.jobs.save(job)
        uow.commit()


def deliver_job(uow: IntegrationManagementUnitOfWork, job_id: uuid.UUID) -> None:
    """Mark a processing job as delivered."""
    with uow:
        job = uow.jobs.get(job_id)
        if job is None:
            raise IntegrationJobNotFoundError(job_id)
        job.mark_delivered()
        uow.jobs.save(job)
        uow.commit()
        logger.info("Delivered integration job %s", job_id)


def fail_job(
    uow: IntegrationManagementUnitOfWork, job_id: uuid.UUID, reason: str
) -> None:
    """Mark a processing job as failed."""
    with uow:
        job = uow.jobs.get(job_id)
        if job is None:
            raise IntegrationJobNotFoundError(job_id)
        job.mark_failed(reason)
        uow.jobs.save(job)
        uow.commit()
        logger.warning("Integration job %s failed: %s", job_id, reason)


def retry_job(uow: IntegrationManagementUnitOfWork, job_id: uuid.UUID) -> None:
    """Retry a failed integration job by re-queuing it."""
    with uow:
        job = uow.jobs.get(job_id)
        if job is None:
            raise IntegrationJobNotFoundError(job_id)
        job.retry()
        uow.jobs.save(job)
        uow.commit()
