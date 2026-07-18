import uuid
from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin

class QuizAttemptAnswer(Base, UUIDMixin):
    __tablename__ = "quiz_attempt_answers"

    attempt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quiz_attempts.id", ondelete="CASCADE"), index=True)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quiz_questions.id"))
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    time_spent_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)

    attempt = relationship("QuizAttempt", back_populates="answers")
