from __future__ import annotations

from collections.abc import Callable

from fastapi import FastAPI

import integration_management.infrastructure.orm  # noqa: F401
import work_management.infrastructure.orm  # noqa: F401
from integration_management.application.use_cases import IntegrationManagementUnitOfWork
from integration_management.infrastructure.api import create_integration_management_router
from integration_management.infrastructure.unit_of_work import (
    SqlAlchemyIntegrationManagementUnitOfWork,
)
from shared.infrastructure.database import create_engine, create_tables
from work_management.application.use_cases import WorkManagementUnitOfWork
from work_management.infrastructure.api import create_work_management_router
from work_management.infrastructure.unit_of_work import (
    SqlAlchemyWorkManagementUnitOfWork,
)


def create_app(
    work_management_uow_factory: Callable[[], WorkManagementUnitOfWork],
    integration_management_uow_factory: Callable[[], IntegrationManagementUnitOfWork],
) -> FastAPI:
    """Create and configure the FastAPI application with all routers."""
    application = FastAPI(title="DDD Onion Hexagonal API")
    application.include_router(create_work_management_router(work_management_uow_factory))
    application.include_router(
        create_integration_management_router(integration_management_uow_factory)
    )
    return application


# Default application instance — run with: uvicorn shared.infrastructure.app:app
_engine = create_engine()
create_tables(_engine)

app = create_app(
    work_management_uow_factory=lambda: SqlAlchemyWorkManagementUnitOfWork(_engine),
    integration_management_uow_factory=lambda: SqlAlchemyIntegrationManagementUnitOfWork(
        _engine
    ),
)
