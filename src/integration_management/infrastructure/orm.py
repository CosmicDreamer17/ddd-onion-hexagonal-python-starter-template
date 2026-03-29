from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared.infrastructure.database import Base


class IntegrationJobModel(Base):
    """SQLAlchemy ORM model for the integration_jobs table."""

    __tablename__ = "integration_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source: Mapped[str] = mapped_column(String(255))
    payload: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20))
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(50))
    updated_at: Mapped[str] = mapped_column(String(50))
