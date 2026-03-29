import abc
import uuid

from integration_management.domain.entities import IntegrationJob
from integration_management.domain.value_objects import JobStatus


class IntegrationJobRepository(abc.ABC):
    """Port interface for IntegrationJob persistence."""

    @abc.abstractmethod
    def get(self, job_id: uuid.UUID) -> IntegrationJob | None: ...

    @abc.abstractmethod
    def save(self, job: IntegrationJob) -> None: ...

    @abc.abstractmethod
    def list(self, *, status: JobStatus | None = None) -> list[IntegrationJob]: ...
