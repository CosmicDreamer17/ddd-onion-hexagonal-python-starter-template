"""Tests for domain events and cross-context communication.

These tests verify that:
1. The event bus correctly dispatches events to handlers
2. WorkItemCompletedEvent triggers integration job creation
3. Cross-context communication works without direct imports
"""

from shared.domain.events import DomainEvent
from shared.infrastructure.event_bus import InMemoryEventBus
from work_management.application.use_cases import (
    activate_work_item,
    assign_work_item,
    complete_work_item,
    create_work_item,
)
from work_management.domain.events import WorkItemCompletedEvent


class TestInMemoryEventBus:
    def test_publishes_to_subscriber(self):
        bus = InMemoryEventBus()
        received = []
        bus.subscribe(WorkItemCompletedEvent, lambda e: received.append(e))

        event = WorkItemCompletedEvent(work_item_id=None, title="test")
        bus.publish(event)

        assert len(received) == 1
        assert received[0] is event

    def test_no_subscribers_does_not_fail(self):
        bus = InMemoryEventBus()
        event = WorkItemCompletedEvent(work_item_id=None, title="test")
        bus.publish(event)  # Should not raise

    def test_multiple_subscribers(self):
        bus = InMemoryEventBus()
        counts = {"a": 0, "b": 0}
        bus.subscribe(
            WorkItemCompletedEvent, lambda e: counts.update(a=counts["a"] + 1)
        )
        bus.subscribe(
            WorkItemCompletedEvent, lambda e: counts.update(b=counts["b"] + 1)
        )

        bus.publish(WorkItemCompletedEvent(work_item_id=None, title="test"))

        assert counts["a"] == 1
        assert counts["b"] == 1

    def test_only_matching_event_type_triggers(self):
        from dataclasses import dataclass

        @dataclass(frozen=True, slots=True)
        class OtherEvent(DomainEvent):
            pass

        bus = InMemoryEventBus()
        received = []
        bus.subscribe(WorkItemCompletedEvent, lambda e: received.append(e))

        bus.publish(OtherEvent())
        assert len(received) == 0

        bus.publish(WorkItemCompletedEvent(work_item_id=None, title="test"))
        assert len(received) == 1


class TestCrossContextEventIntegration:
    """Tests that completing a work item creates an integration job via events."""

    def test_completion_creates_integration_job(
        self, work_management_uow, integration_management_uow, engine
    ):
        from functools import partial

        from integration_management.application.event_handlers import (
            handle_work_item_completed,
        )
        from integration_management.infrastructure.query_adapters import (
            SqlAlchemyIntegrationJobQueryAdapter,
        )

        # Set up event bus with handler
        bus = InMemoryEventBus()
        bus.subscribe(
            WorkItemCompletedEvent,
            partial(handle_work_item_completed, uow=integration_management_uow),
        )

        # Create and complete a work item
        item_id = create_work_item(work_management_uow, "Deliver this")
        assign_work_item(work_management_uow, item_id, "alice@example.com")
        activate_work_item(work_management_uow, item_id)
        complete_work_item(work_management_uow, item_id, event_bus=bus)

        # Verify an integration job was created
        query = SqlAlchemyIntegrationJobQueryAdapter(engine)
        jobs = query.list_by_status()
        assert len(jobs) == 1
        assert "Deliver this" in jobs[0].payload
        assert jobs[0].source == "work_item_completion"
        assert jobs[0].status == "queued"
