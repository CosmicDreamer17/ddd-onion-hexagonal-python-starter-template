from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from integration_management.application.use_cases import (
    IntegrationManagementUnitOfWork,
)
from integration_management.domain.ports import IntegrationJobRepository
from integration_management.infrastructure.repositories import (
    SqlAlchemyIntegrationJobRepository,
)


class SqlAlchemyIntegrationManagementUnitOfWork(IntegrationManagementUnitOfWork):
    """Concrete Unit of Work backed by a SQLAlchemy session."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._session: Session | None = None

    def __enter__(self) -> "SqlAlchemyIntegrationManagementUnitOfWork":
        self._session = Session(self._engine)
        self._jobs = SqlAlchemyIntegrationJobRepository(self._session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        super().__exit__(exc_type, exc_val, exc_tb)
        if self._session is not None:
            self._session.close()

    @property
    def jobs(self) -> IntegrationJobRepository:
        assert self._session is not None, "UoW must be used as a context manager."
        return self._jobs

    def commit(self) -> None:
        assert self._session is not None
        self._session.commit()

    def rollback(self) -> None:
        assert self._session is not None
        self._session.rollback()
