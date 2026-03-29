from __future__ import annotations

import uuid
from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from integration_management.application.use_cases import (
    IntegrationManagementUnitOfWork,
    create_integration_job,
    deliver_job,
    fail_job,
    retry_job,
    start_processing_job,
)
from integration_management.domain.exceptions import InvalidJobTransitionError


class CreateIntegrationJobRequest(BaseModel):
    source: str
    payload: str


class FailJobRequest(BaseModel):
    reason: str


class IntegrationJobResponse(BaseModel):
    id: str
    source: str
    payload: str
    status: str
    error_message: str | None
    created_at: str
    updated_at: str


def create_integration_management_router(
    uow_factory: Callable[[], IntegrationManagementUnitOfWork],
) -> APIRouter:
    """Create a FastAPI router for the integration management bounded context.

    Args:
        uow_factory: Callable that returns a fresh IntegrationManagementUnitOfWork per request.
    """
    router = APIRouter(prefix="/jobs", tags=["jobs"])

    @router.post("", status_code=status.HTTP_201_CREATED)
    def create_job(
        request: CreateIntegrationJobRequest,
        uow: IntegrationManagementUnitOfWork = Depends(uow_factory),
    ) -> dict[str, str]:
        job_id = create_integration_job(uow, request.source, request.payload)
        return {"id": str(job_id)}

    @router.get("/{job_id}", response_model=IntegrationJobResponse)
    def get_job(
        job_id: str,
        uow: IntegrationManagementUnitOfWork = Depends(uow_factory),
    ) -> IntegrationJobResponse:
        try:
            parsed_id = uuid.UUID(job_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Integration job not found.",
            )
        with uow:
            job = uow.jobs.get(parsed_id)
            if job is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Integration job not found.",
                )
            return IntegrationJobResponse(
                id=str(job.id),
                source=job.source,
                payload=job.payload,
                status=job.status.value,
                error_message=job.error_message,
                created_at=job.created_at.isoformat(),
                updated_at=job.updated_at.isoformat(),
            )

    @router.post("/{job_id}/start-processing", status_code=status.HTTP_204_NO_CONTENT)
    def start_processing(
        job_id: str,
        uow: IntegrationManagementUnitOfWork = Depends(uow_factory),
    ) -> None:
        try:
            start_processing_job(uow, uuid.UUID(job_id))
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc
        except InvalidJobTransitionError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=str(exc)
            ) from exc

    @router.post("/{job_id}/deliver", status_code=status.HTTP_204_NO_CONTENT)
    def deliver(
        job_id: str,
        uow: IntegrationManagementUnitOfWork = Depends(uow_factory),
    ) -> None:
        try:
            deliver_job(uow, uuid.UUID(job_id))
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc
        except InvalidJobTransitionError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=str(exc)
            ) from exc

    @router.post("/{job_id}/fail", status_code=status.HTTP_204_NO_CONTENT)
    def fail(
        job_id: str,
        request: FailJobRequest,
        uow: IntegrationManagementUnitOfWork = Depends(uow_factory),
    ) -> None:
        try:
            fail_job(uow, uuid.UUID(job_id), request.reason)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc
        except InvalidJobTransitionError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=str(exc)
            ) from exc

    @router.post("/{job_id}/retry", status_code=status.HTTP_204_NO_CONTENT)
    def retry(
        job_id: str,
        uow: IntegrationManagementUnitOfWork = Depends(uow_factory),
    ) -> None:
        try:
            retry_job(uow, uuid.UUID(job_id))
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc
        except InvalidJobTransitionError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=str(exc)
            ) from exc

    return router
