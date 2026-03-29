from collections import defaultdict

from shared.application.event_bus import EventBus, EventHandler
from shared.domain.events import DomainEvent


class InMemoryEventBus(EventBus):
    """In-memory adapter for synchronous event delivery."""

    def __init__(self) -> None:
        self._handlers: dict[type, list[EventHandler]] = defaultdict(list)

    def publish(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(type(event), []):
            handler(event)

    def subscribe(
        self, event_type: type[DomainEvent], handler: EventHandler
    ) -> None:
        self._handlers[event_type].append(handler)
