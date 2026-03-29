import logging
from collections import defaultdict

from shared.domain.events import DomainEvent, EventBus, EventHandler

logger = logging.getLogger(__name__)


class InMemoryEventBus(EventBus):
    """Synchronous in-memory event bus.

    Dispatches events to registered handlers immediately.
    Suitable for single-process applications. For distributed
    systems, replace with a message broker adapter.
    """

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = defaultdict(list)

    def publish(self, event: DomainEvent) -> None:
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])
        logger.info(
            "Publishing %s (id=%s) to %d handler(s)",
            event_type.__name__,
            event.event_id,
            len(handlers),
        )
        for handler in handlers:
            handler(event)

    def subscribe(self, event_type: type[DomainEvent], handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)
