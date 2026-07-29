"""
CourseForge AI — Notification Service
Responsibility: Manage smart notifications with priority support (critical, high, medium, low).
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.notification import Notification

logger = logging.getLogger(__name__)


class NotificationService:
    """Service to handle user notifications and priority filters."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_notifications(
        self, user_id: str, priority: str | None = None, unread_only: bool = False
    ) -> list[Notification]:
        import uuid
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        except ValueError:
            user_uuid = user_id

        stmt = select(Notification).where(Notification.user_id == user_uuid)
        if priority:
            stmt = stmt.where(Notification.priority == priority)
        if unread_only:
            stmt = stmt.where(Notification.is_read == False)
        stmt = stmt.order_by(Notification.created_at.desc())

        res = await self.db.execute(stmt)
        notifications = res.scalars().all()

        # Generate default notifications if empty
        if not notifications and not priority:
            default_n = Notification(
                user_id=user_uuid,
                type="streak_reminder",
                priority="high",
                title="Keep Your Streak Alive! ⚡",
                body="You're on a 3-day streak. Complete a lesson today to keep momentum.",
                created_at=datetime.now(timezone.utc),
            )
            self.db.add(default_n)
            await self.db.commit()
            return [default_n]

        return notifications

    async def mark_as_read(self, user_id: str, notification_id: str) -> Notification | None:
        import uuid
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
        except ValueError:
            user_uuid = user_id
        try:
            notification_uuid = uuid.UUID(notification_id) if isinstance(notification_id, str) else notification_id
        except ValueError:
            notification_uuid = notification_id

        stmt = select(Notification).where(
            Notification.id == notification_uuid,
            Notification.user_id == user_uuid,
        )
        res = await self.db.execute(stmt)
        n = res.scalar_one_or_none()
        if n:
            n.is_read = True
            self.db.add(n)
            await self.db.commit()
            await self.db.refresh(n)
        return n
