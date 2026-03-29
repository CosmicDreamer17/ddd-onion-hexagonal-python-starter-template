import abc
import uuid

from work_management.application.read_models import WorkItemReadModel


class WorkItemQueryPort(abc.ABC):
    """Port for read-only work item queries.

    Separate from the command-side repository to support CQRS separation.
    Implementations live in the infrastructure layer.
    """

    @abc.abstractmethod
    def get_by_id(self, item_id: uuid.UUID) -> WorkItemReadModel | None: ...

    @abc.abstractmethod
    def list_by_status(self, status: str | None = None) -> list[WorkItemReadModel]: ...


def get_work_item(
    query_port: WorkItemQueryPort, item_id: uuid.UUID
) -> WorkItemReadModel | None:
    """Query a single work item by ID."""
    return query_port.get_by_id(item_id)


def list_work_items(
    query_port: WorkItemQueryPort, status: str | None = None
) -> list[WorkItemReadModel]:
    """List work items, optionally filtered by status."""
    return query_port.list_by_status(status)
