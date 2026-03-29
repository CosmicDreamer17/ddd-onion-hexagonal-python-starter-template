import abc
from typing import Callable

from shared.domain.events import DomainEvent

EventHandler = Callable[[DomainEvent], None]


class EventBus(abc.ABC):
    """Port for publishing and subscribing to domain events."""

    @abc.abstractmethod
    def publish(self, event: DomainEvent) -> None: ...

    @abc.abstractmethod
    def subscribe(
        self, event_type: type[DomainEvent], handler: EventHandler
    ) -> None: ...
