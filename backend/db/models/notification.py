import uuid
from sqlalchemy import Boolean, ForeignKey, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base, UUIDMixin

class Notification(Base, UUIDMixin):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    link: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_ = mapped_column("metadata", JSONB, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), nullable=False)
