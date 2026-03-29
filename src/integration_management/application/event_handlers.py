import uuid

from integration_management.application.use_cases import (
    IntegrationManagementUnitOfWork,
    create_integration_job,
)


def on_work_item_completed(
    work_item_id: uuid.UUID,
    uow: IntegrationManagementUnitOfWork,
) -> uuid.UUID:
    """Creates an integration job for delivery when a work item is completed.

    This handler is wired to WorkItemCompletedEvent at the composition root,
    enabling cross-context communication without direct imports between contexts.
    """
    return create_integration_job(
        uow,
        source="work_management",
        payload=str(work_item_id),
    )
