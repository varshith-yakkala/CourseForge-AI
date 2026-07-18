import uuid
from sqlalchemy import ForeignKey, Integer, String, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class UserProgress(Base, UUIDMixin):
    __tablename__ = "user_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), index=True, nullable=True)
    topic_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=True)
    entity_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    time_spent_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (Index("idx_progress_user_course", "user_id", "course_id"),)
