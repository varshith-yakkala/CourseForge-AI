"""
CourseForge AI — SQLAlchemy Declarative Base

All ORM models import Base from this module.
It is also imported by Alembic's env.py so schema changes are auto-detected.

Usage in model files:
    from db.base import Base

    class User(Base):
        __tablename__ = "users"
        ...
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """
    Shared declarative base for all CourseForge ORM models.
    """


class UUIDMixin:
    """Mixin for UUID primary keys."""
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin for soft-delete support."""
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

