import uuid
from datetime import date
from sqlalchemy import ForeignKey, String, Text, Date
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base, UUIDMixin, TimestampMixin

class WeeklyReport(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "weekly_reports"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    week_start_date = mapped_column(Date, nullable=False)
    summary_md: Mapped[str] = mapped_column(Text, nullable=False)
    metrics_json = mapped_column(JSONB, nullable=True)
