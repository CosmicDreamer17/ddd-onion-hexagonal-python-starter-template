import abc


class AbstractUnitOfWork(abc.ABC):
    """Abstract Unit of Work port.

    Manages transaction boundaries as a context manager.
    Use cases enter the UoW context, perform domain operations,
    and call commit() explicitly on success.
    """

    def __enter__(self) -> "AbstractUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()

    @abc.abstractmethod
    def commit(self) -> None: ...

    @abc.abstractmethod
    def rollback(self) -> None: ...
