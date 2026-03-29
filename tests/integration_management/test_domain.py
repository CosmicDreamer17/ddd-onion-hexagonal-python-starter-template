import pytest

from integration_management.domain.entities import IntegrationJob
from integration_management.domain.exceptions import InvalidJobTransitionError
from integration_management.domain.value_objects import JobStatus


class TestIntegrationJobCreate:
    def test_creates_with_queued_status(self):
        job = IntegrationJob.create("api-source", '{"key": "value"}')
        assert job.status == JobStatus.QUEUED

    def test_creates_with_no_error(self):
        job = IntegrationJob.create("api-source", '{"key": "value"}')
        assert job.error_message is None


class TestIntegrationJobStartProcessing:
    def test_transitions_from_queued(self):
        job = IntegrationJob.create("api-source", "payload")
        job.start_processing()
        assert job.status == JobStatus.PROCESSING

    def test_fails_from_processing(self):
        job = IntegrationJob.create("api-source", "payload")
        job.start_processing()
        with pytest.raises(InvalidJobTransitionError):
            job.start_processing()


class TestIntegrationJobMarkDelivered:
    def test_transitions_from_processing(self):
        job = IntegrationJob.create("api-source", "payload")
        job.start_processing()
        job.mark_delivered()
        assert job.status == JobStatus.DELIVERED

    def test_fails_from_queued(self):
        job = IntegrationJob.create("api-source", "payload")
        with pytest.raises(InvalidJobTransitionError):
            job.mark_delivered()


class TestIntegrationJobMarkFailed:
    def test_transitions_from_processing(self):
        job = IntegrationJob.create("api-source", "payload")
        job.start_processing()
        job.mark_failed("Connection timeout")
        assert job.status == JobStatus.FAILED
        assert job.error_message == "Connection timeout"

    def test_fails_from_queued(self):
        job = IntegrationJob.create("api-source", "payload")
        with pytest.raises(InvalidJobTransitionError):
            job.mark_failed("Error")


class TestIntegrationJobRetry:
    def test_transitions_from_failed_to_queued(self):
        job = IntegrationJob.create("api-source", "payload")
        job.start_processing()
        job.mark_failed("Timeout")
        job.retry()
        assert job.status == JobStatus.QUEUED
        assert job.error_message is None

    def test_fails_from_queued(self):
        job = IntegrationJob.create("api-source", "payload")
        with pytest.raises(InvalidJobTransitionError):
            job.retry()


class TestIntegrationJobFullLifecycle:
    def test_queued_to_processing_to_delivered(self):
        job = IntegrationJob.create("api-source", "payload")
        job.start_processing()
        job.mark_delivered()
        assert job.status == JobStatus.DELIVERED

    def test_queued_to_processing_to_failed_to_retry(self):
        job = IntegrationJob.create("api-source", "payload")
        job.start_processing()
        job.mark_failed("Error")
        assert job.status == JobStatus.FAILED
        job.retry()
        assert job.status == JobStatus.QUEUED
        job.start_processing()
        job.mark_delivered()
        assert job.status == JobStatus.DELIVERED
