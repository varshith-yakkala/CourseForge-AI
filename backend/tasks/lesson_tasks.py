"""
CourseForge AI — Background Lesson Generation Celery Task
"""

from __future__ import annotations

import asyncio
import logging
from tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


async def _generate_lesson_async(course_id: str, lesson_id: str, force: bool = False) -> dict:
    """Async wrapper to process lesson generation in Celery worker."""
    from db.session import get_db_session
    from services.lesson_generator import LessonGeneratorService

    async with get_db_session() as session:
        service = LessonGeneratorService(session)
        lesson = await service.generate_lesson(course_id=course_id, lesson_id=lesson_id, force_regenerate=force)
        return {"status": "success", "lesson_id": str(lesson.id), "version": lesson.version}


@celery_app.task(
    name="tasks.generate_lesson",
    bind=True,
    max_retries=2,
    default_retry_delay=5,
)
def generate_lesson_task(self, course_id: str, lesson_id: str, force: bool = False) -> dict:
    """Celery background task to generate lesson content."""
    try:
        return asyncio.run(_generate_lesson_async(course_id, lesson_id, force))
    except Exception as exc:
        logger.error(f"Task generate_lesson failed for lesson {lesson_id}: {exc}")
        raise self.retry(exc=exc)
