import logging

from integration_management.application.use_cases import (
    IntegrationManagementUnitOfWork,
    create_integration_job,
)
from shared.domain.events import DomainEvent

logger = logging.getLogger(__name__)


def handle_work_item_completed(
    event: DomainEvent,
    uow: IntegrationManagementUnitOfWork,
) -> None:
    """Create a delivery job when a work item is completed.

    This handler demonstrates cross-context communication via domain events.
    It reacts to WorkItemCompletedEvent (from work_management) without
    importing anything from the work_management bounded context.

    The event's data fields are accessed via attribute lookup on the
    generic DomainEvent base class.
    """
    work_item_id = getattr(event, "work_item_id", None)
    title = getattr(event, "title", "unknown")
    logger.info(
        "Handling work item completion: creating delivery job for %s",
        work_item_id,
    )
    create_integration_job(
        uow,
        source="work_item_completion",
        payload=f"Deliver completed work item: {title} (id={work_item_id})",
    )
