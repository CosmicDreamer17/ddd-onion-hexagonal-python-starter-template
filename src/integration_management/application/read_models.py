import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class IntegrationJobReadModel:
    """Read-only projection of an integration job for query responses.

    Separate from the domain entity — no invariant enforcement,
    no mutation methods. Optimized for data transfer.
    """

    id: uuid.UUID
    source: str
    payload: str
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime
