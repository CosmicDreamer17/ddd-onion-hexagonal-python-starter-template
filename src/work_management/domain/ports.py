import abc
import uuid

from work_management.domain.entities import WorkItem
from work_management.domain.value_objects import WorkItemStatus


class WorkItemRepository(abc.ABC):
    """Port interface for WorkItem persistence."""

    @abc.abstractmethod
    def get(self, item_id: uuid.UUID) -> WorkItem | None: ...

    @abc.abstractmethod
    def save(self, work_item: WorkItem) -> None: ...

    @abc.abstractmethod
    def list(self, *, status: WorkItemStatus | None = None) -> list[WorkItem]: ...
