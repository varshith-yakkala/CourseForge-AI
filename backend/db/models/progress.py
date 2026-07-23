import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, Integer, String, Index, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from db.base import Base, UUIDMixin, TimestampMixin

class UserProgress(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), index=True, nullable=True)
    topic_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=True)
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False) # lesson, topic, course
    status: Mapped[str] = mapped_column(String(20), nullable=False) # not_started, in_progress, completed
    
    # Phase 7: Progress Tracking & Metrics
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    completion_percentage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at = mapped_column(DateTime(timezone=True), nullable=True)
    last_opened_at = mapped_column(DateTime(timezone=True), nullable=True)
    last_scroll_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_spent_sec: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)

    __table_args__ = (
        Index("idx_progress_user_course", "user_id", "course_id"),
        Index("idx_progress_user_lesson", "user_id", "lesson_id", unique=True),
    )

