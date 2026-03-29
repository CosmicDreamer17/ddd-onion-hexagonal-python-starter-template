from work_management.application.queries import get_work_item, list_work_items
from work_management.application.use_cases import (
    activate_work_item,
    assign_work_item,
    create_work_item,
)
from work_management.infrastructure.query_adapters import (
    SqlAlchemyWorkItemQueryAdapter,
)


class TestGetWorkItem:
    def test_returns_read_model(self, work_management_uow, engine):
        item_id = create_work_item(work_management_uow, "Test Task")
        query = SqlAlchemyWorkItemQueryAdapter(engine)

        result = get_work_item(query, item_id)

        assert result is not None
        assert result.id == item_id
        assert result.title == "Test Task"
        assert result.status == "pending"

    def test_returns_none_for_missing(self, engine):
        import uuid

        query = SqlAlchemyWorkItemQueryAdapter(engine)
        result = get_work_item(query, uuid.uuid4())
        assert result is None


class TestListWorkItems:
    def test_lists_all(self, work_management_uow, engine):
        create_work_item(work_management_uow, "Task 1")
        create_work_item(work_management_uow, "Task 2")
        query = SqlAlchemyWorkItemQueryAdapter(engine)

        results = list_work_items(query)
        assert len(results) == 2

    def test_filters_by_status(self, work_management_uow, engine):
        id1 = create_work_item(work_management_uow, "Task 1")
        create_work_item(work_management_uow, "Task 2")
        assign_work_item(work_management_uow, id1, "alice@example.com")
        activate_work_item(work_management_uow, id1)

        query = SqlAlchemyWorkItemQueryAdapter(engine)

        active = list_work_items(query, status="active")
        assert len(active) == 1
        assert active[0].status == "active"

        pending = list_work_items(query, status="pending")
        assert len(pending) == 1
        assert pending[0].status == "pending"

    def test_returns_empty_list(self, engine):
        query = SqlAlchemyWorkItemQueryAdapter(engine)
        results = list_work_items(query)
        assert results == []
