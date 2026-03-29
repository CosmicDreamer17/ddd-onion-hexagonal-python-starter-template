import uuid

from work_management.application.queries import get_work_item, list_work_items
from work_management.application.read_models import WorkItemReadModel
from work_management.application.use_cases import (
    activate_work_item,
    assign_work_item,
    create_work_item,
)
from work_management.domain.value_objects import WorkItemStatus


class TestGetWorkItem:
    def test_returns_read_model_for_existing_item(self, work_management_uow):
        item_id = create_work_item(work_management_uow, "My Task")
        result = get_work_item(work_management_uow, item_id)

        assert isinstance(result, WorkItemReadModel)
        assert result.id == item_id
        assert result.title == "My Task"
        assert result.status == WorkItemStatus.PENDING.value
        assert result.assigned_to is None

    def test_returns_none_for_missing_item(self, work_management_uow):
        result = get_work_item(work_management_uow, uuid.uuid4())
        assert result is None

    def test_reflects_assigned_owner(self, work_management_uow):
        item_id = create_work_item(work_management_uow, "My Task")
        assign_work_item(work_management_uow, item_id, "owner@example.com")

        result = get_work_item(work_management_uow, item_id)
        assert result.assigned_to == "owner@example.com"


class TestListWorkItems:
    def test_returns_all_items_when_no_filter(self, work_management_uow):
        create_work_item(work_management_uow, "Task A")
        create_work_item(work_management_uow, "Task B")

        results = list_work_items(work_management_uow)
        assert len(results) == 2
        assert all(isinstance(r, WorkItemReadModel) for r in results)

    def test_filters_by_status(self, work_management_uow):
        item_id = create_work_item(work_management_uow, "Task A")
        create_work_item(work_management_uow, "Task B")
        assign_work_item(work_management_uow, item_id, "owner@example.com")
        activate_work_item(work_management_uow, item_id)

        pending = list_work_items(
            work_management_uow, status_filter=WorkItemStatus.PENDING
        )
        active = list_work_items(
            work_management_uow, status_filter=WorkItemStatus.ACTIVE
        )

        assert len(pending) == 1
        assert pending[0].status == WorkItemStatus.PENDING.value
        assert len(active) == 1
        assert active[0].status == WorkItemStatus.ACTIVE.value

    def test_returns_empty_list_when_no_items(self, work_management_uow):
        results = list_work_items(work_management_uow)
        assert results == []

    def test_status_is_string_not_enum(self, work_management_uow):
        create_work_item(work_management_uow, "Task A")
        results = list_work_items(work_management_uow)
        assert isinstance(results[0].status, str)
