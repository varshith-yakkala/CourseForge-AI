import uuid
from sqlalchemy import ForeignKey, String, Index, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base, UUIDMixin

class AnalyticsEvent(Base, UUIDMixin):
    __tablename__ = "analytics_events"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("courses.id", ondelete="SET NULL"), index=True, nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    metadata_ = mapped_column("metadata", JSONB, nullable=True)
    session_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at = mapped_column(DateTime(timezone=True), index=True, nullable=False)
