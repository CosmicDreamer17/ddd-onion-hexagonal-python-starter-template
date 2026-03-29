from fastapi import FastAPI
from sqlalchemy.engine import Engine

from integration_management.infrastructure.api import (
    create_integration_management_router,
)
from integration_management.infrastructure.unit_of_work import (
    SqlAlchemyIntegrationManagementUnitOfWork,
)
from shared.infrastructure.database import Base, create_engine
from work_management.infrastructure.api import create_work_management_router
from work_management.infrastructure.unit_of_work import (
    SqlAlchemyWorkManagementUnitOfWork,
)


def create_app(engine: Engine | None = None) -> FastAPI:
    """Application factory. Creates a fully wired FastAPI app.

    Args:
        engine: SQLAlchemy engine. If None, creates a default SQLite engine.
    """
    if engine is None:
        engine = create_engine()

    # Import ORM models to register with Base metadata
    import integration_management.infrastructure.orm  # noqa: F401
    import work_management.infrastructure.orm  # noqa: F401

    Base.metadata.create_all(engine)

    app = FastAPI(
        title="DDD Onion Hexagonal Starter",
        description="DDD/Onion/Hexagonal Architecture starter template",
        version="0.1.0",
    )

    # Wire up bounded context routers with their UoW instances
    work_uow = SqlAlchemyWorkManagementUnitOfWork(engine)
    integration_uow = SqlAlchemyIntegrationManagementUnitOfWork(engine)

    app.include_router(create_work_management_router(work_uow))
    app.include_router(create_integration_management_router(integration_uow))

    return app
