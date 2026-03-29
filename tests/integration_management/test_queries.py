import uuid

from integration_management.application.queries import (
    get_integration_job,
    list_integration_jobs,
)
from integration_management.application.read_models import IntegrationJobReadModel
from integration_management.application.use_cases import (
    create_integration_job,
    start_processing_job,
)
from integration_management.domain.value_objects import JobStatus


class TestGetIntegrationJob:
    def test_returns_read_model_for_existing_job(self, integration_management_uow):
        job_id = create_integration_job(
            integration_management_uow, "api-source", "payload-data"
        )
        result = get_integration_job(integration_management_uow, job_id)

        assert isinstance(result, IntegrationJobReadModel)
        assert result.id == job_id
        assert result.source == "api-source"
        assert result.payload == "payload-data"
        assert result.status == JobStatus.QUEUED.value
        assert result.error_message is None

    def test_returns_none_for_missing_job(self, integration_management_uow):
        result = get_integration_job(integration_management_uow, uuid.uuid4())
        assert result is None

    def test_reflects_status_change(self, integration_management_uow):
        job_id = create_integration_job(
            integration_management_uow, "api-source", "payload"
        )
        start_processing_job(integration_management_uow, job_id)

        result = get_integration_job(integration_management_uow, job_id)
        assert result.status == JobStatus.PROCESSING.value


class TestListIntegrationJobs:
    def test_returns_all_jobs_when_no_filter(self, integration_management_uow):
        create_integration_job(integration_management_uow, "source-a", "payload-a")
        create_integration_job(integration_management_uow, "source-b", "payload-b")

        results = list_integration_jobs(integration_management_uow)
        assert len(results) == 2
        assert all(isinstance(r, IntegrationJobReadModel) for r in results)

    def test_filters_by_status(self, integration_management_uow):
        job_id = create_integration_job(
            integration_management_uow, "source-a", "payload-a"
        )
        create_integration_job(integration_management_uow, "source-b", "payload-b")
        start_processing_job(integration_management_uow, job_id)

        queued = list_integration_jobs(
            integration_management_uow, status_filter=JobStatus.QUEUED
        )
        processing = list_integration_jobs(
            integration_management_uow, status_filter=JobStatus.PROCESSING
        )

        assert len(queued) == 1
        assert queued[0].status == JobStatus.QUEUED.value
        assert len(processing) == 1
        assert processing[0].status == JobStatus.PROCESSING.value

    def test_returns_empty_list_when_no_jobs(self, integration_management_uow):
        results = list_integration_jobs(integration_management_uow)
        assert results == []

    def test_status_is_string_not_enum(self, integration_management_uow):
        create_integration_job(integration_management_uow, "source-a", "payload-a")
        results = list_integration_jobs(integration_management_uow)
        assert isinstance(results[0].status, str)
