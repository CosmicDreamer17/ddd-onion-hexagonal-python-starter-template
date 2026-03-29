import abc
import uuid

from shared.application.event_bus import EventBus
from shared.application.unit_of_work import AbstractUnitOfWork
from work_management.domain.entities import WorkItem
from work_management.domain.events import WorkItemActivatedEvent, WorkItemCompletedEvent
from work_management.domain.ports import WorkItemRepository


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
        return item.id


def assign_work_item(
    uow: WorkManagementUnitOfWork, item_id: uuid.UUID, owner_email: str
) -> None:
    """Assign an owner to a work item."""
    with uow:
        item = uow.work_items.get(item_id)
        if item is None:
            raise ValueError(f"WorkItem {item_id} not found.")
        item.assign_owner(owner_email)
        uow.work_items.save(item)
        uow.commit()


def activate_work_item(
    uow: WorkManagementUnitOfWork,
    item_id: uuid.UUID,
    event_bus: EventBus | None = None,
) -> None:
    """Activate a work item. Requires an assigned owner.

    Publishes WorkItemActivatedEvent if an event_bus is provided.
    """
    with uow:
        item = uow.work_items.get(item_id)
        if item is None:
            raise ValueError(f"WorkItem {item_id} not found.")
        item.activate()
        uow.work_items.save(item)
        uow.commit()
    if event_bus is not None:
        event_bus.publish(WorkItemActivatedEvent(work_item_id=item.id))


def complete_work_item(
    uow: WorkManagementUnitOfWork,
    item_id: uuid.UUID,
    event_bus: EventBus | None = None,
) -> None:
    """Complete an active work item.

    Publishes WorkItemCompletedEvent if an event_bus is provided.
    """
    with uow:
        item = uow.work_items.get(item_id)
        if item is None:
            raise ValueError(f"WorkItem {item_id} not found.")
        item.complete()
        uow.work_items.save(item)
        uow.commit()
    if event_bus is not None:
        event_bus.publish(WorkItemCompletedEvent(work_item_id=item.id))
