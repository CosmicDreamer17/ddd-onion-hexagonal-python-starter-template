import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class IntegrationJobReadModel:
    """Read model for integration job query responses.

    Simple data container with no invariant enforcement.
    Status is represented as a plain string (the enum value).
    """

    id: uuid.UUID
    source: str
    payload: str
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime
