import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from integration_management.application.use_cases import (
    IntegrationManagementUnitOfWork,
    create_integration_job,
    deliver_job,
    fail_job,
    retry_job,
    start_processing_job,
)
from integration_management.domain.exceptions import (
    IntegrationManagementError,
    InvalidJobTransitionError,
)


class CreateJobRequest(BaseModel):
    source: str
    payload: str


class CreateJobResponse(BaseModel):
    id: uuid.UUID


class FailJobRequest(BaseModel):
    reason: str


def create_integration_management_router(
    uow: IntegrationManagementUnitOfWork,
) -> APIRouter:
    """Factory that creates a FastAPI router wired to the given UoW."""
    router = APIRouter(prefix="/integration-jobs", tags=["integration-jobs"])

    @router.post("", response_model=CreateJobResponse, status_code=201)
    def create(request: CreateJobRequest) -> CreateJobResponse:
        job_id = create_integration_job(uow, request.source, request.payload)
        return CreateJobResponse(id=job_id)

    @router.post("/{job_id}/start", status_code=204)
    def start(job_id: uuid.UUID) -> None:
        try:
            start_processing_job(uow, job_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None
        except InvalidJobTransitionError as e:
            raise HTTPException(status_code=409, detail=str(e)) from None

    @router.post("/{job_id}/deliver", status_code=204)
    def deliver(job_id: uuid.UUID) -> None:
        try:
            deliver_job(uow, job_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None
        except IntegrationManagementError as e:
            raise HTTPException(status_code=409, detail=str(e)) from None

    @router.post("/{job_id}/fail", status_code=204)
    def fail(job_id: uuid.UUID, request: FailJobRequest) -> None:
        try:
            fail_job(uow, job_id, request.reason)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None
        except IntegrationManagementError as e:
            raise HTTPException(status_code=409, detail=str(e)) from None

    @router.post("/{job_id}/retry", status_code=204)
    def retry(job_id: uuid.UUID) -> None:
        try:
            retry_job(uow, job_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None
        except IntegrationManagementError as e:
            raise HTTPException(status_code=409, detail=str(e)) from None

    return router
