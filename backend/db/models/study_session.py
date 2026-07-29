import uuid
from sqlalchemy import ForeignKey, DateTime, Integer, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class StudySession(Base, UUIDMixin):
    __tablename__ = "study_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    
    started_at = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_pomodoro: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    topics_covered = mapped_column(JSON, nullable=True)
    quizzes_taken: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    flashcards_reviewed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    questions_asked: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user = relationship("User")
    course = relationship("Course")
