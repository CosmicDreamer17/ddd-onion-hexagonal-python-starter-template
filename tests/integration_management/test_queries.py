from integration_management.application.queries import (
    get_integration_job,
    list_integration_jobs,
)
from integration_management.application.use_cases import (
    create_integration_job,
    start_processing_job,
)
from integration_management.infrastructure.query_adapters import (
    SqlAlchemyIntegrationJobQueryAdapter,
)


class TestGetIntegrationJob:
    def test_returns_read_model(self, integration_management_uow, engine):
        job_id = create_integration_job(
            integration_management_uow, "api-source", "payload"
        )
        query = SqlAlchemyIntegrationJobQueryAdapter(engine)

        result = get_integration_job(query, job_id)

        assert result is not None
        assert result.id == job_id
        assert result.source == "api-source"
        assert result.status == "queued"

    def test_returns_none_for_missing(self, engine):
        import uuid

        query = SqlAlchemyIntegrationJobQueryAdapter(engine)
        result = get_integration_job(query, uuid.uuid4())
        assert result is None


class TestListIntegrationJobs:
    def test_lists_all(self, integration_management_uow, engine):
        create_integration_job(integration_management_uow, "src1", "p1")
        create_integration_job(integration_management_uow, "src2", "p2")
        query = SqlAlchemyIntegrationJobQueryAdapter(engine)

        results = list_integration_jobs(query)
        assert len(results) == 2

    def test_filters_by_status(self, integration_management_uow, engine):
        job_id = create_integration_job(integration_management_uow, "src1", "p1")
        create_integration_job(integration_management_uow, "src2", "p2")
        start_processing_job(integration_management_uow, job_id)

        query = SqlAlchemyIntegrationJobQueryAdapter(engine)

        processing = list_integration_jobs(query, status="processing")
        assert len(processing) == 1

        queued = list_integration_jobs(query, status="queued")
        assert len(queued) == 1
