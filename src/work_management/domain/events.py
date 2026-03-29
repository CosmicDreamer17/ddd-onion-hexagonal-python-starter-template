import uuid
from dataclasses import dataclass

from shared.domain.events import DomainEvent


@dataclass(frozen=True, kw_only=True)
class WorkItemActivatedEvent(DomainEvent):
    """Published when a work item transitions to ACTIVE status."""

    work_item_id: uuid.UUID


@dataclass(frozen=True, kw_only=True)
class WorkItemCompletedEvent(DomainEvent):
    """Published when a work item transitions to COMPLETED status."""

    work_item_id: uuid.UUID
