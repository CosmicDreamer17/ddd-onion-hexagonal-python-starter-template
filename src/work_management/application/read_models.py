import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class WorkItemReadModel:
    """Read model for work item query responses.

    Simple data container with no invariant enforcement.
    Status is represented as a plain string (the enum value).
    """

    id: uuid.UUID
    title: str
    status: str
    assigned_to: str | None
    created_at: datetime
    updated_at: datetime
