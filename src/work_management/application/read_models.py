import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class WorkItemReadModel:
    """Read-only projection of a work item for query responses.

    Separate from the domain entity — no invariant enforcement,
    no mutation methods. Optimized for data transfer.
    """

    id: uuid.UUID
    title: str
    status: str
    assigned_to: str | None
    version: int
    created_at: datetime
    updated_at: datetime
