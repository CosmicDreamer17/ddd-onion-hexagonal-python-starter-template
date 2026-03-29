from unittest.mock import MagicMock

from work_management.application.use_cases import (
    activate_work_item,
    assign_work_item,
    complete_work_item,
    create_work_item,
)
from work_management.domain.events import WorkItemActivatedEvent, WorkItemCompletedEvent


class TestActivateWorkItemPublishesEvent:
    def test_publishes_activated_event(self, work_management_uow, event_bus):
        handler = MagicMock()
        event_bus.subscribe(WorkItemActivatedEvent, handler)

        item_id = create_work_item(work_management_uow, "Test Task")
        assign_work_item(work_management_uow, item_id, "alice@example.com")
        activate_work_item(work_management_uow, item_id, event_bus=event_bus)

        handler.assert_called_once()
        event = handler.call_args[0][0]
        assert isinstance(event, WorkItemActivatedEvent)
        assert event.work_item_id == item_id

    def test_no_event_without_bus(self, work_management_uow):
        item_id = create_work_item(work_management_uow, "Test Task")
        assign_work_item(work_management_uow, item_id, "alice@example.com")
        activate_work_item(work_management_uow, item_id)

    def test_does_not_publish_completed_on_activate(self, work_management_uow, event_bus):
        completed_handler = MagicMock()
        event_bus.subscribe(WorkItemCompletedEvent, completed_handler)

        item_id = create_work_item(work_management_uow, "Test Task")
        assign_work_item(work_management_uow, item_id, "alice@example.com")
        activate_work_item(work_management_uow, item_id, event_bus=event_bus)

        completed_handler.assert_not_called()


class TestCompleteWorkItemPublishesEvent:
    def test_publishes_completed_event(self, work_management_uow, event_bus):
        handler = MagicMock()
        event_bus.subscribe(WorkItemCompletedEvent, handler)

        item_id = create_work_item(work_management_uow, "Test Task")
        assign_work_item(work_management_uow, item_id, "alice@example.com")
        activate_work_item(work_management_uow, item_id)
        complete_work_item(work_management_uow, item_id, event_bus=event_bus)

        handler.assert_called_once()
        event = handler.call_args[0][0]
        assert isinstance(event, WorkItemCompletedEvent)
        assert event.work_item_id == item_id

    def test_no_event_without_bus(self, work_management_uow):
        item_id = create_work_item(work_management_uow, "Test Task")
        assign_work_item(work_management_uow, item_id, "alice@example.com")
        activate_work_item(work_management_uow, item_id)
        complete_work_item(work_management_uow, item_id)

    def test_does_not_publish_activated_on_complete(self, work_management_uow, event_bus):
        activated_handler = MagicMock()
        event_bus.subscribe(WorkItemActivatedEvent, activated_handler)

        item_id = create_work_item(work_management_uow, "Test Task")
        assign_work_item(work_management_uow, item_id, "alice@example.com")
        activate_work_item(work_management_uow, item_id)
        complete_work_item(work_management_uow, item_id, event_bus=event_bus)

        activated_handler.assert_not_called()
