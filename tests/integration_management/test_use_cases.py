import uuid

import pytest

from integration_management.application.use_cases import (
    create_integration_job,
    deliver_job,
    fail_job,
    retry_job,
    start_processing_job,
)
from integration_management.domain.value_objects import JobStatus


class TestCreateIntegrationJob:
    def test_creates_and_returns_id(self, integration_management_uow):
        job_id = create_integration_job(
            integration_management_uow, "api-source", "payload"
        )
        assert job_id is not None

    def test_persists_job(self, integration_management_uow):
        job_id = create_integration_job(
            integration_management_uow, "api-source", "payload"
        )
        with integration_management_uow:
            job = integration_management_uow.jobs.get(job_id)
            assert job is not None
            assert job.source == "api-source"
            assert job.status == JobStatus.QUEUED


class TestStartProcessingJob:
    def test_starts_processing(self, integration_management_uow):
        job_id = create_integration_job(
            integration_management_uow, "api-source", "payload"
        )
        start_processing_job(integration_management_uow, job_id)

        with integration_management_uow:
            job = integration_management_uow.jobs.get(job_id)
            assert job.status == JobStatus.PROCESSING

    def test_raises_for_nonexistent_job(self, integration_management_uow):
        with pytest.raises(ValueError, match="not found"):
            start_processing_job(integration_management_uow, uuid.uuid4())


class TestDeliverJob:
    def test_delivers_processing_job(self, integration_management_uow):
        job_id = create_integration_job(
            integration_management_uow, "api-source", "payload"
        )
        start_processing_job(integration_management_uow, job_id)
        deliver_job(integration_management_uow, job_id)

        with integration_management_uow:
            job = integration_management_uow.jobs.get(job_id)
            assert job.status == JobStatus.DELIVERED


class TestFailAndRetryJob:
    def test_fail_and_retry_lifecycle(self, integration_management_uow):
        job_id = create_integration_job(
            integration_management_uow, "api-source", "payload"
        )
        start_processing_job(integration_management_uow, job_id)
        fail_job(integration_management_uow, job_id, "Timeout")

        with integration_management_uow:
            job = integration_management_uow.jobs.get(job_id)
            assert job.status == JobStatus.FAILED
            assert job.error_message == "Timeout"

        retry_job(integration_management_uow, job_id)

        with integration_management_uow:
            job = integration_management_uow.jobs.get(job_id)
            assert job.status == JobStatus.QUEUED
            assert job.error_message is None
