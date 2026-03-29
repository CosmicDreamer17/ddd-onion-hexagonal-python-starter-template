import pytest
from sqlalchemy import create_engine as sa_create_engine
from sqlalchemy.engine import Engine

from shared.infrastructure.database import create_tables


@pytest.fixture
def engine() -> Engine:
    e = sa_create_engine("sqlite:///:memory:")
    # Import ORM models so they register with Base metadata
    import integration_management.infrastructure.orm  # noqa: F401
    import work_management.infrastructure.orm  # noqa: F401

    create_tables(e)
    return e


@pytest.fixture
def work_management_uow(engine: Engine):
    from work_management.infrastructure.unit_of_work import (
        SqlAlchemyWorkManagementUnitOfWork,
    )

    return SqlAlchemyWorkManagementUnitOfWork(engine)


@pytest.fixture
def integration_management_uow(engine: Engine):
    from integration_management.infrastructure.unit_of_work import (
        SqlAlchemyIntegrationManagementUnitOfWork,
    )

    return SqlAlchemyIntegrationManagementUnitOfWork(engine)
