"""
CourseForge AI — Study Planner Service
Responsibility: Manage adaptive study plans, calculate dynamic daily schedules, and generate multi-event learning calendar data.
"""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.study_plan import StudyPlan
from db.models.course import Course
from db.models.lesson import Lesson
from db.models.progress import UserProgress
from db.models.flashcard import Flashcard
from db.models.flashcard_review import FlashcardReview
from db.models.quiz import Quiz

logger = logging.getLogger(__name__)


class StudyPlannerService:
    """Service to generate adaptive study schedules and calendar timeline events."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_plan(
        self,
        user_id: str,
        course_id: str,
        daily_goal_min: int = 30,
        weekly_goal_min: int = 210,
        target_date: date | None = None,
        preferred_days: list[str] | None = None,
    ) -> StudyPlan:
        stmt = select(StudyPlan).where(
            StudyPlan.user_id == user_id,
            StudyPlan.course_id == course_id,
        )
        res = await self.db.execute(stmt)
        plan = res.scalar_one_or_none()

        if not plan:
            if not target_date:
                target_date = date.today() + timedelta(days=21)
            plan = StudyPlan(
                user_id=user_id,
                course_id=course_id,
                daily_goal_min=daily_goal_min,
                weekly_goal_min=weekly_goal_min,
                target_completion_date=target_date,
                preferred_study_days=preferred_days or ["Mon", "Tue", "Wed", "Thu", "Fri"],
            )
            self.db.add(plan)
            await self.db.commit()
            await self.db.refresh(plan)
        return plan

    async def update_plan(
        self,
        user_id: str,
        course_id: str,
        daily_goal_min: int,
        target_date: date | None = None,
        preferred_days: list[str] | None = None,
    ) -> StudyPlan:
        plan = await self.get_or_create_plan(user_id, course_id)
        plan.daily_goal_min = daily_goal_min
        plan.weekly_goal_min = daily_goal_min * 7
        if target_date:
            plan.target_completion_date = target_date
        if preferred_days:
            plan.preferred_study_days = preferred_days

        self.db.add(plan)
        await self.db.commit()
        await self.db.refresh(plan)
        return plan

    async def get_adaptive_schedule(self, user_id: str, course_id: str) -> dict:
        """
        Calculates adaptive schedule based on uncompleted lessons and remaining days.
        """
        plan = await self.get_or_create_plan(user_id, course_id)

        # Get all lessons
        stmt_l = select(Lesson).where(Lesson.course_id == course_id).order_by(Lesson.order_index)
        res_l = await self.db.execute(stmt_l)
        lessons = res_l.scalars().all()

        # Get completed progress
        stmt_p = select(UserProgress).where(
            UserProgress.user_id == user_id,
            UserProgress.course_id == course_id,
            UserProgress.completed == True,
        )
        res_p = await self.db.execute(stmt_p)
        completed_progress = res_p.scalars().all()
        completed_ids = {p.lesson_id for p in completed_progress}

        uncompleted = [l for l in lessons if l.id not in completed_ids]

        daily_blocks = []
        current_day = date.today()

        for idx, lesson in enumerate(uncompleted):
            block_date = current_day + timedelta(days=idx)
            daily_blocks.append({
                "day_name": block_date.strftime("%a, %b %d"),
                "date": block_date.isoformat(),
                "title": f"Study: {lesson.title}",
                "activity_type": "lesson",
                "estimated_mins": lesson.estimated_duration_min or plan.daily_goal_min,
                "lesson_id": str(lesson.id),
            })

            # Add quiz block every 2 lessons
            if (idx + 1) % 2 == 0:
                daily_blocks.append({
                    "day_name": block_date.strftime("%a, %b %d"),
                    "date": block_date.isoformat(),
                    "title": f"Assessment: Quiz for {lesson.title}",
                    "activity_type": "quiz",
                    "estimated_mins": 10,
                    "lesson_id": str(lesson.id),
                })

        remaining_mins = sum(b["estimated_mins"] for b in daily_blocks)
        remaining_hours = round(remaining_mins / 60, 1)

        estimated_finish = date.today() + timedelta(days=max(len(uncompleted), 1))

        return {
            "daily_goal_min": plan.daily_goal_min,
            "target_completion_date": plan.target_completion_date.isoformat() if plan.target_completion_date else None,
            "estimated_completion_date": estimated_finish.isoformat(),
            "remaining_uncompleted_lessons": len(uncompleted),
            "remaining_hours": remaining_hours,
            "schedule_blocks": daily_blocks,
        }

    async def get_calendar_events(self, user_id: str, course_id: str) -> list[dict]:
        """
        Multi-event visual calendar data (Study Session, Lesson, Quiz, Flashcards, Deadline).
        """
        schedule = await self.get_adaptive_schedule(user_id, course_id)
        events = []

        # Add planned daily blocks
        for block in schedule.get("schedule_blocks", []):
            events.append({
                "id": f"event_{block['date']}_{block['lesson_id']}",
                "title": block["title"],
                "date": block["date"],
                "event_type": block["activity_type"], # lesson, quiz, flashcards
                "status": "planned",
            })

        # Add Flashcards Due event today
        events.append({
            "id": "event_flashcards_today",
            "title": "Flashcards Spaced Repetition Due",
            "date": date.today().isoformat(),
            "event_type": "flashcards",
            "status": "due",
        })

        # Add Target Deadline event
        if schedule.get("target_completion_date"):
            events.append({
                "id": "event_deadline",
                "title": "🎯 Target Course Completion Deadline",
                "date": schedule["target_completion_date"],
                "event_type": "deadline",
                "status": "upcoming",
            })

        return events
