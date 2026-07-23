"""
CourseForge AI — Background Lesson Generation Service
"""


from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


async def generate_lesson(course_id: str, lesson_id: str, force: bool = False) -> dict:
    """Async service function to process lesson generation synchronously."""
    from db.session import get_db_session
    from services.lesson_generator import LessonGeneratorService

    async with get_db_session() as session:
        service = LessonGeneratorService(session)
        lesson = await service.generate_lesson(course_id=course_id, lesson_id=lesson_id, force_regenerate=force)
        return {"status": "success", "lesson_id": str(lesson.id), "version": lesson.version}


# Alias for backward compatibility
_generate_lesson_async = generate_lesson


