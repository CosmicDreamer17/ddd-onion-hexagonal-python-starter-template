from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from work_management.application.use_cases import WorkManagementUnitOfWork
from work_management.domain.ports import WorkItemRepository
from work_management.infrastructure.repositories import SqlAlchemyWorkItemRepository


class SqlAlchemyWorkManagementUnitOfWork(WorkManagementUnitOfWork):
    """Concrete Unit of Work backed by a SQLAlchemy session."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine
        self._session: Session | None = None

    def __enter__(self) -> "SqlAlchemyWorkManagementUnitOfWork":
        self._session = Session(self._engine)
        self._work_items = SqlAlchemyWorkItemRepository(self._session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        super().__exit__(exc_type, exc_val, exc_tb)
        if self._session is not None:
            self._session.close()

    @property
    def work_items(self) -> WorkItemRepository:
        assert self._session is not None, "UoW must be used as a context manager."
        return self._work_items

    def commit(self) -> None:
        assert self._session is not None
        self._session.commit()

    def rollback(self) -> None:
        assert self._session is not None
        self._session.rollback()
