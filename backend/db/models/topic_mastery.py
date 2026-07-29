import uuid
from sqlalchemy import ForeignKey, String, Float, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.base import Base, UUIDMixin, TimestampMixin

class TopicMastery(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "topic_mastery"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    topic_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), index=True, nullable=True)
    
    mastery_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False) # 0.0 to 1.0
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    consecutive_successes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_difficulty: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    weakness_concepts = mapped_column(JSON, nullable=True)

    user = relationship("User")
    course = relationship("Course")
    topic = relationship("Topic")
