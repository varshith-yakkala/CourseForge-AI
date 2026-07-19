import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, Text, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from db.base import Base, UUIDMixin

class UserAchievement(Base, UUIDMixin):
    __tablename__ = "user_achievements"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    badge_key: Mapped[str] = mapped_column(String(50), nullable=False) # first_lesson, quiz_master, 7_day_streak, flashcard_expert, course_completed, ai_explorer
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon_name: Mapped[str] = mapped_column(String(50), default="Award", nullable=False)
    unlocked_at = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_user_badge", "user_id", "badge_key", unique=True),
    )
