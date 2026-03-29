import abc
import logging
import uuid

from shared.application.unit_of_work import AbstractUnitOfWork
from shared.domain.events import EventBus
from work_management.domain.entities import WorkItem
from work_management.domain.events import WorkItemCompletedEvent
from work_management.domain.exceptions import WorkItemNotFoundError
from work_management.domain.ports import WorkItemRepository

logger = logging.getLogger(__name__)


class WorkManagementUnitOfWork(AbstractUnitOfWork):
    """Port defining the unit of work for the work management bounded context."""

    @property
    @abc.abstractmethod
    def work_items(self) -> WorkItemRepository: ...


def create_work_item(uow: WorkManagementUnitOfWork, title: str) -> uuid.UUID:
    """Create a new work item in PENDING status."""
    with uow:
        item = WorkItem.create(title)
        uow.work_items.save(item)
        uow.commit()
        logger.info("Created work item %s: %s", item.id, title)
        return item.id


def assign_work_item(
    uow: WorkManagementUnitOfWork, item_id: uuid.UUID, owner_email: str
) -> None:
    """Assign an owner to a work item."""
    with uow:
        item = uow.work_items.get(item_id)
        if item is None:
            raise WorkItemNotFoundError(item_id)
        item.assign_owner(owner_email)
        uow.work_items.save(item)
        uow.commit()


def activate_work_item(uow: WorkManagementUnitOfWork, item_id: uuid.UUID) -> None:
    """Activate a work item. Requires an assigned owner."""
    with uow:
        item = uow.work_items.get(item_id)
        if item is None:
            raise WorkItemNotFoundError(item_id)
        item.activate()
        uow.work_items.save(item)
        uow.commit()
        logger.info("Activated work item %s", item_id)


def complete_work_item(
    uow: WorkManagementUnitOfWork,
    item_id: uuid.UUID,
    event_bus: EventBus | None = None,
) -> None:
    """Complete an active work item. Optionally publishes a completion event."""
    with uow:
        item = uow.work_items.get(item_id)
        if item is None:
            raise WorkItemNotFoundError(item_id)
        item.complete()
        uow.work_items.save(item)
        uow.commit()
        logger.info("Completed work item %s", item_id)
        if event_bus is not None:
            event_bus.publish(
                WorkItemCompletedEvent(
                    work_item_id=item.id,
                    title=item.title,
                )
            )
