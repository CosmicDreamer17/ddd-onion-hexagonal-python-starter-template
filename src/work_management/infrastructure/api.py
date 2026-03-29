import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from work_management.application.queries import (
    WorkItemQueryPort,
    get_work_item,
    list_work_items,
)
from work_management.application.read_models import WorkItemReadModel
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
    WorkItemNotFoundError,
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
    created_at: str
    updated_at: str


def create_work_management_router(
    uow: WorkManagementUnitOfWork,
    query_adapter: WorkItemQueryPort,
) -> APIRouter:
    """Create a FastAPI router wired to the given UoW and query adapter."""
    router = APIRouter(prefix="/work-items", tags=["work-items"])

    @router.get("", response_model=list[WorkItemResponse])
    def list_items(status: str | None = None) -> list[WorkItemResponse]:
        items = list_work_items(query_adapter, status)
        return [_to_response(item) for item in items]

    @router.get("/{item_id}", response_model=WorkItemResponse)
    def get_item(item_id: uuid.UUID) -> WorkItemResponse:
        item = get_work_item(query_adapter, item_id)
        if item is None:
            raise HTTPException(
                status_code=404, detail=f"WorkItem {item_id} not found."
            )
        return _to_response(item)

    @router.post("", response_model=CreateWorkItemResponse, status_code=201)
    def create(request: CreateWorkItemRequest) -> CreateWorkItemResponse:
        item_id = create_work_item(uow, request.title)
        return CreateWorkItemResponse(id=item_id)

    @router.post("/{item_id}/assign", status_code=204)
    def assign(item_id: uuid.UUID, request: AssignWorkItemRequest) -> None:
        try:
            assign_work_item(uow, item_id, request.owner_email)
        except WorkItemNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None
        except InvalidOwnerEmailError as e:
            raise HTTPException(status_code=422, detail=str(e)) from None

    @router.post("/{item_id}/activate", status_code=204)
    def activate(item_id: uuid.UUID) -> None:
        try:
            activate_work_item(uow, item_id)
        except WorkItemNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None
        except (OwnerRequiredError, InvalidStateTransitionError) as e:
            raise HTTPException(status_code=409, detail=str(e)) from None

    @router.post("/{item_id}/complete", status_code=204)
    def complete(item_id: uuid.UUID) -> None:
        try:
            complete_work_item(uow, item_id)
        except WorkItemNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None
        except InvalidStateTransitionError as e:
            raise HTTPException(status_code=409, detail=str(e)) from None

    return router


def _to_response(item: WorkItemReadModel) -> WorkItemResponse:
    return WorkItemResponse(
        id=item.id,
        title=item.title,
        status=item.status,
        assigned_to=item.assigned_to,
        version=item.version,
        created_at=item.created_at.isoformat(),
        updated_at=item.updated_at.isoformat(),
    )
