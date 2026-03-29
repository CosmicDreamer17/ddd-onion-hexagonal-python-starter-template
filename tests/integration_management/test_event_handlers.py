import uuid

from integration_management.application.event_handlers import on_work_item_completed
from integration_management.domain.value_objects import JobStatus


class TestOnWorkItemCompleted:
    def test_creates_integration_job(self, integration_management_uow):
        work_item_id = uuid.uuid4()
        job_id = on_work_item_completed(work_item_id, integration_management_uow)

        assert job_id is not None
        with integration_management_uow:
            job = integration_management_uow.jobs.get(job_id)
        assert job is not None
        assert job.source == "work_management"
        assert job.payload == str(work_item_id)
        assert job.status == JobStatus.QUEUED

    def test_each_call_creates_distinct_job(self, integration_management_uow):
        id_a = on_work_item_completed(uuid.uuid4(), integration_management_uow)
        id_b = on_work_item_completed(uuid.uuid4(), integration_management_uow)

        assert id_a != id_b
