import uuid
from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, Index, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class QuizAttempt(Base, UUIDMixin):
    __tablename__ = "quiz_attempts"

    quiz_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    started_at = mapped_column(DateTime(timezone=True), nullable=False)
    submitted_at = mapped_column(DateTime(timezone=True), nullable=True)
    score_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    time_taken_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)

    quiz = relationship("Quiz", back_populates="attempts")
    answers = relationship("QuizAttemptAnswer", back_populates="attempt", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_quiz_attempts_user_quiz", "user_id", "quiz_id"),)
