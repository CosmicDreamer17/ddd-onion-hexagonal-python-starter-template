import abc
import uuid

from integration_management.application.read_models import IntegrationJobReadModel


class IntegrationJobQueryPort(abc.ABC):
    """Port for read-only integration job queries.

    Separate from the command-side repository to support CQRS separation.
    Implementations live in the infrastructure layer.
    """

    @abc.abstractmethod
    def get_by_id(self, job_id: uuid.UUID) -> IntegrationJobReadModel | None: ...

    @abc.abstractmethod
    def list_by_status(
        self, status: str | None = None
    ) -> list[IntegrationJobReadModel]: ...


def get_integration_job(
    query_port: IntegrationJobQueryPort, job_id: uuid.UUID
) -> IntegrationJobReadModel | None:
    """Query a single integration job by ID."""
    return query_port.get_by_id(job_id)


def list_integration_jobs(
    query_port: IntegrationJobQueryPort, status: str | None = None
) -> list[IntegrationJobReadModel]:
    """List integration jobs, optionally filtered by status."""
    return query_port.list_by_status(status)
