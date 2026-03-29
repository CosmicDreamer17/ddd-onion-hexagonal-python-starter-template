from sqlalchemy import create_engine as sa_create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models across bounded contexts."""


def create_engine(url: str = "sqlite:///app.db") -> Engine:
    return sa_create_engine(url)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine)


def create_tables(engine: Engine) -> None:
    Base.metadata.create_all(engine)
