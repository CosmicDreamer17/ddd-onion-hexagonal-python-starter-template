import uuid
from dataclasses import dataclass

from shared.domain.events import DomainEvent


@dataclass(frozen=True, slots=True)
class WorkItemCompletedEvent(DomainEvent):
    """Published when a work item transitions to COMPLETED status.

    Integration management can subscribe to this event to automatically
    create a delivery job for the completed work.
    """

    work_item_id: uuid.UUID = None  # type: ignore[assignment]
    title: str = ""
