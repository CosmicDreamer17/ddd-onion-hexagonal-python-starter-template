import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from work_management.domain.exceptions import (
    InvalidOwnerEmailError,
    InvalidStateTransitionError,
    OwnerRequiredError,
)
from work_management.domain.value_objects import WorkItemStatus


@dataclass(slots=True)
class WorkItem:
    """Core aggregate root for the Work Management bounded context.

    Represents a unit of work with lifecycle state invariants.
    All state transitions are enforced through domain methods.
    """

    id: uuid.UUID
    title: str
    status: WorkItemStatus
    version: int
    assigned_to: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, title: str) -> "WorkItem":
        now = datetime.now(UTC)
        return cls(
            id=uuid.uuid4(),
            title=title,
            status=WorkItemStatus.PENDING,
            version=1,
            assigned_to=None,
            created_at=now,
            updated_at=now,
        )

    def assign_owner(self, owner_email: str) -> None:
        if not owner_email or "@" not in owner_email:
            raise InvalidOwnerEmailError
        self.assigned_to = owner_email
        self.updated_at = datetime.now(UTC)
        self.version += 1

    def activate(self) -> None:
        if self.status != WorkItemStatus.PENDING:
            raise InvalidStateTransitionError(
                self.status.value, WorkItemStatus.ACTIVE.value
            )
        if not self.assigned_to:
            raise OwnerRequiredError
        self.status = WorkItemStatus.ACTIVE
        self.updated_at = datetime.now(UTC)
        self.version += 1

    def complete(self) -> None:
        if self.status != WorkItemStatus.ACTIVE:
            raise InvalidStateTransitionError(
                self.status.value, WorkItemStatus.COMPLETED.value
            )
        self.status = WorkItemStatus.COMPLETED
        self.updated_at = datetime.now(UTC)
        self.version += 1
