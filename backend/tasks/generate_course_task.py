"""Course generation background task."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

async def generate_course(course_id: str) -> dict:
    """Async service function to generate course blueprint synchronously."""
    from db.session import get_db_session
    from db.models.course import Course
    from sqlalchemy import select
    from services.course_generator import CourseGeneratorService
    from core.exceptions import CourseForgeError

    async with get_db_session() as session:
        # 1. Update status to generating
        stmt = select(Course).where(Course.id == course_id)
        result = await session.execute(stmt)
        course = result.scalar_one_or_none()
        
        if not course:
            logger.error(f"Course {course_id} not found.")
            return {"status": "error"}
            
        course.status = "generating_outline"
        course.generation_error = None
        session.add(course)
        await session.commit()
        
        try:
            # 2. Run Blueprint Generation
            service = CourseGeneratorService(session)
            await service.generate_blueprint(course_id)
            
            logger.info(f"Course {course_id} blueprint generated successfully.")
            return {"status": "success"}
        except CourseForgeError as e:
            logger.error(f"Failed to generate course {course_id}: {e}")
            course.status = "error"
            course.generation_error = str(e)
            session.add(course)
            await session.commit()
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating course {course_id}: {e}")
            course.status = "error"
            course.generation_error = str(e)
            session.add(course)
            await session.commit()
            raise


# Alias for backward compatibility
_generate_course_async = generate_course


