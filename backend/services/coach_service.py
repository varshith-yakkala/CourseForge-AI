"""
CourseForge AI — AI Coach Service
Responsibility: Proactively generate AI coaching tips and guidance with lightweight interaction memory.
"""
from __future__ import annotations

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

# Lightweight in-memory coach interaction history cache (user_id -> last_message)
COACH_MEMORY: dict[str, str] = {}


class AICoachService:
    """Service to provide proactive AI Learning Coach guidance."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.analytics_service = AnalyticsService(db)

    async def get_coach_advice(self, user_id: str, course_id: str | None = None) -> dict:
        """
        Generates contextual coaching tip string. Remembers previous message to avoid repetition.
        """
        last_msg = COACH_MEMORY.get(user_id, "")

        if course_id:
            analytics = await self.analytics_service.get_course_analytics(user_id, course_id)
            completed = analytics.get("completed_lessons", 0)
            total = analytics.get("total_lessons", 1)
            streak = analytics.get("learning_streak_days", 1)

            if completed == 0:
                tip = "Welcome! Let's get started on your first lesson today to build momentum."
            elif completed < total:
                tip = f"Awesome work! You've completed {completed} of {total} lessons. Keep your {streak}-day streak alive by opening the next lesson!"
            else:
                tip = "Congratulations! You've completed all lessons in this course. Retake quizzes or review flashcards to maintain mastery."
        else:
            tip = "Keep up the momentum! Review flashcards daily to boost your long-term memory retention."

        # Rotate tip if identical to memory
        if tip == last_msg:
            tip = "Pro tip: Taking 5-minute quiz reviews after completing a lesson doubles your recall accuracy!"

        COACH_MEMORY[user_id] = tip

        return {
            "tip": tip,
            "coach_name": "CourseForge AI Coach",
            "avatar_icon": "Sparkles",
            "previous_message": last_msg or None,
        }
