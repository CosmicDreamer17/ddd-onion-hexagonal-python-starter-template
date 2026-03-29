"""End-to-end test demonstrating cross-context event-driven communication.

work_management completes a work item → publishes WorkItemCompletedEvent via shared
EventBus → integration_management handler auto-creates an integration job.

No direct imports between bounded contexts — all coordination flows through the
shared EventBus, wired at the composition root (here: test setup).
"""

from integration_management.application.event_handlers import on_work_item_completed
from integration_management.domain.value_objects import JobStatus
from work_management.application.use_cases import (
    activate_work_item,
    assign_work_item,
    complete_work_item,
    create_work_item,
)
from work_management.domain.events import WorkItemActivatedEvent, WorkItemCompletedEvent


class TestCrossContextEventFlow:
    def test_completing_work_item_triggers_integration_job(
        self, work_management_uow, integration_management_uow, event_bus
    ):
        created_job_ids: list = []

        # Composition root: wire work_management events → integration_management handler
        event_bus.subscribe(
            WorkItemCompletedEvent,
            lambda e: created_job_ids.append(
                on_work_item_completed(e.work_item_id, integration_management_uow)
            ),
        )

        item_id = create_work_item(work_management_uow, "Deploy feature")
        assign_work_item(work_management_uow, item_id, "alice@example.com")
        activate_work_item(work_management_uow, item_id)
        complete_work_item(work_management_uow, item_id, event_bus=event_bus)

        assert len(created_job_ids) == 1
        with integration_management_uow:
            job = integration_management_uow.jobs.get(created_job_ids[0])
        assert job is not None
        assert job.source == "work_management"
        assert job.payload == str(item_id)
        assert job.status == JobStatus.QUEUED

    def test_activating_does_not_trigger_integration_job(
        self, work_management_uow, integration_management_uow, event_bus
    ):
        created_job_ids: list = []

        event_bus.subscribe(
            WorkItemCompletedEvent,
            lambda e: created_job_ids.append(
                on_work_item_completed(e.work_item_id, integration_management_uow)
            ),
        )
        event_bus.subscribe(WorkItemActivatedEvent, lambda e: None)

        item_id = create_work_item(work_management_uow, "Deploy feature")
        assign_work_item(work_management_uow, item_id, "alice@example.com")
        activate_work_item(work_management_uow, item_id, event_bus=event_bus)

        assert len(created_job_ids) == 0
