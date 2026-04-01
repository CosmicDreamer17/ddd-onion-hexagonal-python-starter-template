import pytest

from work_management.domain.entities import WorkItem
from work_management.domain.exceptions import (
    InvalidOwnerEmailError,
    InvalidStateTransitionError,
    OwnerRequiredError,
)
from work_management.domain.value_objects import WorkItemStatus


class TestWorkItemCreate:
    def test_creates_with_pending_status(self):
        item = WorkItem.create("Test Task")
        assert item.status == WorkItemStatus.PENDING

    def test_creates_with_no_owner(self):
        item = WorkItem.create("Test Task")
        assert item.assigned_to is None

    def test_creates_with_version_one(self):
        item = WorkItem.create("Test Task")
        assert item.version == 1


class TestWorkItemAssignOwner:
    def test_assigns_valid_owner(self):
        item = WorkItem.create("Test Task")
        item.assign_owner("alice@example.com")
        assert item.assigned_to == "alice@example.com"

    def test_increments_version(self):
        item = WorkItem.create("Test Task")
        item.assign_owner("alice@example.com")
        assert item.version == 2

    def test_rejects_empty_email(self):
        item = WorkItem.create("Test Task")
        with pytest.raises(InvalidOwnerEmailError):
            item.assign_owner("")

    def test_rejects_email_without_at(self):
        item = WorkItem.create("Test Task")
        with pytest.raises(InvalidOwnerEmailError):
            item.assign_owner("invalid-email")


class TestWorkItemActivate:
    def test_activates_when_assigned(self):
        item = WorkItem.create("Test Task")
        item.assign_owner("alice@example.com")
        item.activate()
        assert item.status == WorkItemStatus.ACTIVE

    def test_fails_without_owner(self):
        item = WorkItem.create("Test Task")
        with pytest.raises(OwnerRequiredError):
            item.activate()

    def test_fails_from_active_status(self):
        item = WorkItem.create("Test Task")
        item.assign_owner("alice@example.com")
        item.activate()
        with pytest.raises(InvalidStateTransitionError):
            item.activate()

    def test_fails_from_completed_status(self):
        item = WorkItem.create("Test Task")
        item.assign_owner("alice@example.com")
        item.activate()
        item.complete()
        with pytest.raises(InvalidStateTransitionError):
            item.activate()


class TestWorkItemComplete:
    def test_completes_active_item(self):
        item = WorkItem.create("Test Task")
        item.assign_owner("alice@example.com")
        item.activate()
        item.complete()
        assert item.status == WorkItemStatus.COMPLETED

    def test_fails_from_pending_status(self):
        item = WorkItem.create("Test Task")
        with pytest.raises(InvalidStateTransitionError):
            item.complete()


class TestWorkItemFullLifecycle:
    def test_pending_to_active_to_completed(self):
        item = WorkItem.create("Full Lifecycle")
        assert item.status == WorkItemStatus.PENDING

        item.assign_owner("alice@example.com")
        item.activate()
        assert item.status == WorkItemStatus.ACTIVE

        item.complete()
        assert item.status == WorkItemStatus.COMPLETED
        assert item.version == 4  # create(1) + assign(2) + activate(3) + complete(4)
