import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from integration_management.application.queries import (
    IntegrationJobQueryPort,
    get_integration_job,
    list_integration_jobs,
)
from integration_management.application.read_models import IntegrationJobReadModel
from integration_management.application.use_cases import (
    IntegrationManagementUnitOfWork,
    create_integration_job,
    deliver_job,
    fail_job,
    retry_job,
    start_processing_job,
)
from integration_management.domain.exceptions import (
    IntegrationJobNotFoundError,
    InvalidJobTransitionError,
)


class CreateJobRequest(BaseModel):
    source: str
    payload: str


class CreateJobResponse(BaseModel):
    id: uuid.UUID


class FailJobRequest(BaseModel):
    reason: str


class IntegrationJobResponse(BaseModel):
    id: uuid.UUID
    source: str
    payload: str
    status: str
    error_message: str | None
    created_at: str
    updated_at: str


def create_integration_management_router(
    uow: IntegrationManagementUnitOfWork,
    query_adapter: IntegrationJobQueryPort,
) -> APIRouter:
    """Create a FastAPI router wired to the given UoW and query adapter."""
    router = APIRouter(prefix="/integration-jobs", tags=["integration-jobs"])

    @router.get("", response_model=list[IntegrationJobResponse])
    def list_jobs(status: str | None = None) -> list[IntegrationJobResponse]:
        jobs = list_integration_jobs(query_adapter, status)
        return [_to_response(job) for job in jobs]

    @router.get("/{job_id}", response_model=IntegrationJobResponse)
    def get_job(job_id: uuid.UUID) -> IntegrationJobResponse:
        job = get_integration_job(query_adapter, job_id)
        if job is None:
            raise HTTPException(
                status_code=404,
                detail=f"IntegrationJob {job_id} not found.",
            )
        return _to_response(job)

    @router.post("", response_model=CreateJobResponse, status_code=201)
    def create(request: CreateJobRequest) -> CreateJobResponse:
        job_id = create_integration_job(uow, request.source, request.payload)
        return CreateJobResponse(id=job_id)

    @router.post("/{job_id}/start", status_code=204)
    def start(job_id: uuid.UUID) -> None:
        try:
            start_processing_job(uow, job_id)
        except IntegrationJobNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None
        except InvalidJobTransitionError as e:
            raise HTTPException(status_code=409, detail=str(e)) from None

    @router.post("/{job_id}/deliver", status_code=204)
    def deliver(job_id: uuid.UUID) -> None:
        try:
            deliver_job(uow, job_id)
        except IntegrationJobNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None
        except InvalidJobTransitionError as e:
            raise HTTPException(status_code=409, detail=str(e)) from None

    @router.post("/{job_id}/fail", status_code=204)
    def fail(job_id: uuid.UUID, request: FailJobRequest) -> None:
        try:
            fail_job(uow, job_id, request.reason)
        except IntegrationJobNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None
        except InvalidJobTransitionError as e:
            raise HTTPException(status_code=409, detail=str(e)) from None

    @router.post("/{job_id}/retry", status_code=204)
    def retry(job_id: uuid.UUID) -> None:
        try:
            retry_job(uow, job_id)
        except IntegrationJobNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None
        except InvalidJobTransitionError as e:
            raise HTTPException(status_code=409, detail=str(e)) from None

    return router


def _to_response(job: IntegrationJobReadModel) -> IntegrationJobResponse:
    return IntegrationJobResponse(
        id=job.id,
        source=job.source,
        payload=job.payload,
        status=job.status,
        error_message=job.error_message,
        created_at=job.created_at.isoformat(),
        updated_at=job.updated_at.isoformat(),
    )
