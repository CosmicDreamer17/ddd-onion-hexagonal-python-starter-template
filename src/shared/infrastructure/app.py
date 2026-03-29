import logging
import os
from functools import partial

from fastapi import FastAPI
from sqlalchemy.engine import Engine

from integration_management.application.event_handlers import (
    handle_work_item_completed,
)
from integration_management.infrastructure.api import (
    create_integration_management_router,
)
from integration_management.infrastructure.query_adapters import (
    SqlAlchemyIntegrationJobQueryAdapter,
)
from integration_management.infrastructure.unit_of_work import (
    SqlAlchemyIntegrationManagementUnitOfWork,
)
from shared.infrastructure.database import Base, create_engine
from shared.infrastructure.event_bus import InMemoryEventBus
from work_management.domain.events import WorkItemCompletedEvent
from work_management.infrastructure.api import create_work_management_router
from work_management.infrastructure.query_adapters import (
    SqlAlchemyWorkItemQueryAdapter,
)
from work_management.infrastructure.unit_of_work import (
    SqlAlchemyWorkManagementUnitOfWork,
)


def create_app(engine: Engine | None = None) -> FastAPI:
    """Application factory. Creates a fully wired FastAPI app.

    Args:
        engine: SQLAlchemy engine. If None, creates a default SQLite engine.
    """
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=log_level, format="%(levelname)s %(name)s: %(message)s")
    logger = logging.getLogger(__name__)

    if engine is None:
        engine = create_engine()

    logger.info("Starting application")

    # Import ORM models to register with Base metadata
    import integration_management.infrastructure.orm  # noqa: F401
    import work_management.infrastructure.orm  # noqa: F401

    Base.metadata.create_all(engine)

    app = FastAPI(
        title="DDD Onion Hexagonal Starter",
        version="0.1.0",
    )

    # Health check
    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    # Wire up event bus for cross-context communication
    event_bus = InMemoryEventBus()
    integration_uow = SqlAlchemyIntegrationManagementUnitOfWork(engine)

    event_bus.subscribe(
        WorkItemCompletedEvent,
        partial(handle_work_item_completed, uow=integration_uow),
    )

    # Wire up bounded context routers
    work_uow = SqlAlchemyWorkManagementUnitOfWork(engine)
    work_query = SqlAlchemyWorkItemQueryAdapter(engine)
    app.include_router(create_work_management_router(work_uow, work_query, event_bus))

    integration_query = SqlAlchemyIntegrationJobQueryAdapter(engine)
    app.include_router(
        create_integration_management_router(integration_uow, integration_query)
    )

    return app
