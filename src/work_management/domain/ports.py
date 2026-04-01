import abc
import uuid

from work_management.domain.entities import WorkItem


class WorkItemRepository(abc.ABC):
    """Port interface for WorkItem persistence."""

    @abc.abstractmethod
    def get(self, item_id: uuid.UUID) -> WorkItem | None: ...

    @abc.abstractmethod
    def save(self, work_item: WorkItem) -> None: ...
