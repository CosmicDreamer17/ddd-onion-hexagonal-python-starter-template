import abc
import uuid

from integration_management.domain.entities import IntegrationJob


class IntegrationJobRepository(abc.ABC):
    """Port interface for IntegrationJob persistence."""

    @abc.abstractmethod
    def get(self, job_id: uuid.UUID) -> IntegrationJob | None: ...

    @abc.abstractmethod
    def save(self, job: IntegrationJob) -> None: ...
