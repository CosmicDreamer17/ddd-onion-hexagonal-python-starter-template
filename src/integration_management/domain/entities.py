import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from integration_management.domain.exceptions import InvalidJobTransitionError
from integration_management.domain.value_objects import JobStatus


@dataclass(slots=True)
class IntegrationJob:
    """Aggregate root for the Integration Management bounded context.

    Represents an external integration job with lifecycle:
    QUEUED -> PROCESSING -> DELIVERED or FAILED.
    Failed jobs can be retried (FAILED -> QUEUED).
    """

    id: uuid.UUID
    source: str
    payload: str
    status: JobStatus
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, source: str, payload: str) -> "IntegrationJob":
        now = datetime.now(UTC)
        return cls(
            id=uuid.uuid4(),
            source=source,
            payload=payload,
            status=JobStatus.QUEUED,
            error_message=None,
            created_at=now,
            updated_at=now,
        )

    def start_processing(self) -> None:
        if self.status != JobStatus.QUEUED:
            raise InvalidJobTransitionError(
                self.status.value, JobStatus.PROCESSING.value
            )
        self.status = JobStatus.PROCESSING
        self.updated_at = datetime.now(UTC)

    def mark_delivered(self) -> None:
        if self.status != JobStatus.PROCESSING:
            raise InvalidJobTransitionError(
                self.status.value, JobStatus.DELIVERED.value
            )
        self.status = JobStatus.DELIVERED
        self.updated_at = datetime.now(UTC)

    def mark_failed(self, reason: str) -> None:
        if self.status != JobStatus.PROCESSING:
            raise InvalidJobTransitionError(self.status.value, JobStatus.FAILED.value)
        self.status = JobStatus.FAILED
        self.error_message = reason
        self.updated_at = datetime.now(UTC)

    def retry(self) -> None:
        if self.status != JobStatus.FAILED:
            raise InvalidJobTransitionError(self.status.value, JobStatus.QUEUED.value)
        self.status = JobStatus.QUEUED
        self.error_message = None
        self.updated_at = datetime.now(UTC)
