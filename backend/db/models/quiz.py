import uuid
from sqlalchemy import Boolean, ForeignKey, Integer, String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin, TimestampMixin

class Quiz(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "quizzes"

    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), unique=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id"), index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    pass_score_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=70.0, nullable=False)
    time_limit_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    shuffle_questions: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    lesson = relationship("Lesson", back_populates="quiz")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")
