from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from shared.infrastructure.database import Base


class WorkItemModel(Base):
    """SQLAlchemy ORM model for the work_items table."""

    __tablename__ = "work_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20))
    assigned_to: Mapped[str | None] = mapped_column(String(255), nullable=True)
    version: Mapped[int]
    created_at: Mapped[str] = mapped_column(String(50))
    updated_at: Mapped[str] = mapped_column(String(50))
