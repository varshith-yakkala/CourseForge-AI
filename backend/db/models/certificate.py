import uuid
from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from db.base import Base, UUIDMixin

class Certificate(Base, UUIDMixin):
    __tablename__ = "certificates"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"))
    issued_at = mapped_column(DateTime(timezone=True), nullable=False)
    certificate_url: Mapped[str] = mapped_column(Text, nullable=False)
    verification_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "course_id"),)
