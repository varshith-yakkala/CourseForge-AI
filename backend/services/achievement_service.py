"""
CourseForge AI — Achievement Service
Responsibility: Evaluate student milestones and unlock achievement badges.
"""
from __future__ import annotations

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.achievement import UserAchievement
from db.models.progress import UserProgress
from db.models.quiz_attempt import QuizAttempt
from db.models.flashcard_review import FlashcardReview

logger = logging.getLogger(__name__)


BADGE_DEFINITIONS = {
    "first_lesson": {
        "title": "First Step Taken",
        "description": "Completed your first lesson in CourseForge AI.",
        "icon_name": "BookOpen",
    },
    "quiz_master": {
        "title": "Quiz Master",
        "description": "Passed a quiz with a score of 80% or higher.",
        "icon_name": "Award",
    },
    "7_day_streak": {
        "title": "7-Day Streak",
        "description": "Learned consistently 7 days in a row.",
        "icon_name": "Zap",
    },
    "flashcard_expert": {
        "title": "Flashcard Expert",
        "description": "Reviewed over 20 flashcards using spaced repetition.",
        "icon_name": "Layers",
    },
    "course_completed": {
        "title": "Course Champion",
        "description": "Completed 100% of lessons in a course.",
        "icon_name": "CheckCircle2",
    },
    "ai_explorer": {
        "title": "AI Explorer",
        "description": "Asked the AI Tutor a question about a lesson.",
        "icon_name": "Sparkles",
    },
}


class AchievementService:
    """Service to evaluate user progress and grant badges."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_achievements(self, user_id: str) -> list[UserAchievement]:
        stmt = select(UserAchievement).where(UserAchievement.user_id == user_id).order_by(UserAchievement.unlocked_at.desc())
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def check_and_unlock(self, user_id: str, badge_key: str) -> UserAchievement | None:
        if badge_key not in BADGE_DEFINITIONS:
            return None

        stmt = select(UserAchievement).where(
            UserAchievement.user_id == user_id,
            UserAchievement.badge_key == badge_key,
        )
        res = await self.db.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing:
            return existing

        def_data = BADGE_DEFINITIONS[badge_key]
        achievement = UserAchievement(
            user_id=user_id,
            badge_key=badge_key,
            title=def_data["title"],
            description=def_data["description"],
            icon_name=def_data["icon_name"],
        )
        self.db.add(achievement)
        await self.db.commit()
        await self.db.refresh(achievement)
        return achievement
