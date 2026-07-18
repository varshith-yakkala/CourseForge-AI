import uuid
from sqlalchemy import ForeignKey, Integer, String, Text, ARRAY, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin, TimestampMixin

class QuizQuestion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "quiz_questions"

    quiz_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), index=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(20), nullable=False)
    options = mapped_column(JSONB, nullable=True)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(20), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    source_chunk_ids = mapped_column(ARRAY(Text), nullable=True)

    quiz = relationship("Quiz", back_populates="questions")
