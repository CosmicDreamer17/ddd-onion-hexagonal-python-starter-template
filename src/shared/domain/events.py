import abc
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Base class for all domain events.

    Events are immutable records of something that happened in the domain.
    They carry the data needed for handlers to react without coupling
    to the originating bounded context.
    """

    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


EventHandler = Callable[[DomainEvent], None]


class EventBus(abc.ABC):
    """Port for publishing and subscribing to domain events.

    Enables cross-context communication without direct imports.
    Each bounded context publishes events; other contexts subscribe
    handlers for events they care about.
    """

    @abc.abstractmethod
    def publish(self, event: DomainEvent) -> None: ...

    @abc.abstractmethod
    def subscribe(
        self, event_type: type[DomainEvent], handler: EventHandler
    ) -> None: ...
