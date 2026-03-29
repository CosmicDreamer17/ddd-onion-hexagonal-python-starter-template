import uuid

from fastapi import APIRouter, HTTPException
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
    WorkManagementError,
)


class CreateWorkItemRequest(BaseModel):
    title: str


class CreateWorkItemResponse(BaseModel):
    id: uuid.UUID


class AssignWorkItemRequest(BaseModel):
    owner_email: str


class WorkItemResponse(BaseModel):
    id: uuid.UUID
    title: str
    status: str
    assigned_to: str | None
    version: int


def create_work_management_router(
    uow: WorkManagementUnitOfWork,
) -> APIRouter:
    """Factory that creates a FastAPI router wired to the given UoW."""
    router = APIRouter(prefix="/work-items", tags=["work-items"])

    @router.post("", response_model=CreateWorkItemResponse, status_code=201)
    def create(request: CreateWorkItemRequest) -> CreateWorkItemResponse:
        item_id = create_work_item(uow, request.title)
        return CreateWorkItemResponse(id=item_id)

    @router.post("/{item_id}/assign", status_code=204)
    def assign(item_id: uuid.UUID, request: AssignWorkItemRequest) -> None:
        try:
            assign_work_item(uow, item_id, request.owner_email)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None
        except InvalidOwnerEmailError as e:
            raise HTTPException(status_code=422, detail=str(e)) from None

    @router.post("/{item_id}/activate", status_code=204)
    def activate(item_id: uuid.UUID) -> None:
        try:
            activate_work_item(uow, item_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None
        except OwnerRequiredError as e:
            raise HTTPException(status_code=409, detail=str(e)) from None
        except InvalidStateTransitionError as e:
            raise HTTPException(status_code=409, detail=str(e)) from None

    @router.post("/{item_id}/complete", status_code=204)
    def complete(item_id: uuid.UUID) -> None:
        try:
            complete_work_item(uow, item_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None
        except WorkManagementError as e:
            raise HTTPException(status_code=409, detail=str(e)) from None

    return router
