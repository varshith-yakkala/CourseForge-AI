import uuid
from datetime import date
from sqlalchemy import ForeignKey, Integer, String, Date, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base, UUIDMixin, TimestampMixin

class StudyPlan(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "study_plans"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    daily_goal_min: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    weekly_goal_min: Mapped[int] = mapped_column(Integer, default=210, nullable=False)
    target_completion_date = mapped_column(Date, nullable=True)
    preferred_study_days = mapped_column(ARRAY(String), nullable=True) # ["Mon", "Wed", "Fri"]
    preferred_study_time: Mapped[str | None] = mapped_column(String(50), nullable=True) # "Evening (7 PM - 9 PM)"
    difficulty_pref: Mapped[str] = mapped_column(String(20), default="Intermediate", nullable=False)
