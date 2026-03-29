import pytest

from work_management.application.use_cases import (
    activate_work_item,
    assign_work_item,
    complete_work_item,
    create_work_item,
)
from work_management.domain.exceptions import OwnerRequiredError
from work_management.domain.value_objects import WorkItemStatus


class TestCreateWorkItem:
    def test_creates_and_returns_id(self, work_management_uow):
        item_id = create_work_item(work_management_uow, "Test Task")
        assert item_id is not None

    def test_persists_work_item(self, work_management_uow):
        item_id = create_work_item(work_management_uow, "Test Task")
        with work_management_uow:
            item = work_management_uow.work_items.get(item_id)
            assert item is not None
            assert item.title == "Test Task"
            assert item.status == WorkItemStatus.PENDING


class TestAssignWorkItem:
    def test_assigns_owner(self, work_management_uow):
        item_id = create_work_item(work_management_uow, "Test Task")
        assign_work_item(work_management_uow, item_id, "alice@example.com")

        with work_management_uow:
            item = work_management_uow.work_items.get(item_id)
            assert item.assigned_to == "alice@example.com"

    def test_raises_for_nonexistent_item(self, work_management_uow):
        import uuid

        with pytest.raises(ValueError, match="not found"):
            assign_work_item(work_management_uow, uuid.uuid4(), "alice@example.com")


class TestActivateWorkItem:
    def test_activates_assigned_item(self, work_management_uow):
        item_id = create_work_item(work_management_uow, "Test Task")
        assign_work_item(work_management_uow, item_id, "alice@example.com")
        activate_work_item(work_management_uow, item_id)

        with work_management_uow:
            item = work_management_uow.work_items.get(item_id)
            assert item.status == WorkItemStatus.ACTIVE

    def test_fails_without_assignment(self, work_management_uow):
        item_id = create_work_item(work_management_uow, "Test Task")
        with pytest.raises(OwnerRequiredError):
            activate_work_item(work_management_uow, item_id)


class TestCompleteWorkItem:
    def test_completes_active_item(self, work_management_uow):
        item_id = create_work_item(work_management_uow, "Test Task")
        assign_work_item(work_management_uow, item_id, "alice@example.com")
        activate_work_item(work_management_uow, item_id)
        complete_work_item(work_management_uow, item_id)

        with work_management_uow:
            item = work_management_uow.work_items.get(item_id)
            assert item.status == WorkItemStatus.COMPLETED
