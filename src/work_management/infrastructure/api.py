from __future__ import annotations

import uuid
from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from work_management.application.use_cases import (
    WorkManagementUnitOfWork,
    activate_work_item,
    assign_work_item,
    complete_work_item,
    create_work_item,
)
from work_management.domain.exceptions import (
    InvalidOwnerEmailError,
    InvalidStateTransitionError,
    OwnerRequiredError,
)


class CreateWorkItemRequest(BaseModel):
    title: str


class AssignWorkItemRequest(BaseModel):
    owner_email: str


class WorkItemResponse(BaseModel):
    id: str
    title: str
    status: str
    assigned_to: str | None
    version: int
    created_at: str
    updated_at: str


def create_work_management_router(
    uow_factory: Callable[[], WorkManagementUnitOfWork],
) -> APIRouter:
    """Create a FastAPI router for the work management bounded context.

    Args:
        uow_factory: Callable that returns a fresh WorkManagementUnitOfWork per request.
    """
    router = APIRouter(prefix="/work-items", tags=["work-items"])

    @router.post("", status_code=status.HTTP_201_CREATED)
    def create_item(
        request: CreateWorkItemRequest,
        uow: WorkManagementUnitOfWork = Depends(uow_factory),
    ) -> dict[str, str]:
        item_id = create_work_item(uow, request.title)
        return {"id": str(item_id)}

    @router.get("/{item_id}", response_model=WorkItemResponse)
    def get_item(
        item_id: str,
        uow: WorkManagementUnitOfWork = Depends(uow_factory),
    ) -> WorkItemResponse:
        try:
            parsed_id = uuid.UUID(item_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Work item not found.",
            )
        with uow:
            item = uow.work_items.get(parsed_id)
            if item is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Work item not found.",
                )
            return WorkItemResponse(
                id=str(item.id),
                title=item.title,
                status=item.status.value,
                assigned_to=item.assigned_to,
                version=item.version,
                created_at=item.created_at.isoformat(),
                updated_at=item.updated_at.isoformat(),
            )

    @router.post("/{item_id}/assign", status_code=status.HTTP_204_NO_CONTENT)
    def assign_item(
        item_id: str,
        request: AssignWorkItemRequest,
        uow: WorkManagementUnitOfWork = Depends(uow_factory),
    ) -> None:
        try:
            assign_work_item(uow, uuid.UUID(item_id), request.owner_email)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc
        except InvalidOwnerEmailError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
            ) from exc

    @router.post("/{item_id}/activate", status_code=status.HTTP_204_NO_CONTENT)
    def activate_item(
        item_id: str,
        uow: WorkManagementUnitOfWork = Depends(uow_factory),
    ) -> None:
        try:
            activate_work_item(uow, uuid.UUID(item_id))
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc
        except OwnerRequiredError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
            ) from exc
        except InvalidStateTransitionError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=str(exc)
            ) from exc

    @router.post("/{item_id}/complete", status_code=status.HTTP_204_NO_CONTENT)
    def complete_item(
        item_id: str,
        uow: WorkManagementUnitOfWork = Depends(uow_factory),
    ) -> None:
        try:
            complete_work_item(uow, uuid.UUID(item_id))
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc
        except InvalidStateTransitionError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=str(exc)
            ) from exc

    return router
