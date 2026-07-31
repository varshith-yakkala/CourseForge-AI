"""Course generation background task."""
from __future__ import annotations

import logging
import uuid

logger = logging.getLogger(__name__)

async def generate_course(course_id: str | uuid.UUID) -> dict:
    """Async service function to generate course blueprint synchronously."""
    from db.session import get_db_session
    from db.models.course import Course
    from sqlalchemy import select
    import uuid
    from services.course_generator import CourseGeneratorService
    from core.exceptions import CourseForgeError

    try:
        course_uuid = uuid.UUID(course_id) if isinstance(course_id, str) else course_id
    except ValueError:
        course_uuid = course_id

    async with get_db_session() as session:
        # 1. Update status to generating
        stmt = select(Course).where(Course.id == course_uuid)
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
            course.status = "failed"
            course.generation_error = str(e)
            session.add(course)
            await session.commit()
            raise CourseForgeError(detail=str(e.detail if hasattr(e, 'detail') else e), status_code=400)
        except Exception as e:
            logger.error(f"Unexpected error generating course {course_id}: {e}")
            course.status = "failed"
            course.generation_error = str(e)
            session.add(course)
            await session.commit()
            raise CourseForgeError(detail=f"Course generation failed: {str(e)}", status_code=400)


# Alias for backward compatibility
_generate_course_async = generate_course


