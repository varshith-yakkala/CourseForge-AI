"""Course routes."""
import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.deps import get_current_active_user, get_db
from api.courses.schemas import CourseCreate, CourseUpdate, CourseResponse
from core.rate_limit import limiter, _get_user_or_ip
from db.models.course import Course
from db.models.lesson import Lesson
from db.models.topic import Topic
from db.models.subtopic import Subtopic
from db.models.user import User

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.get("", response_model=list[CourseResponse])
async def list_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> Any:
    """Retrieve all courses owned by the current user."""
    stmt = select(Course).where(
        Course.owner_id == current_user.id,
        Course.deleted_at.is_(None)
    ).order_by(Course.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    courses = result.scalars().all()
    return courses


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    *,
    db: AsyncSession = Depends(get_db),
    course_in: CourseCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Create a new empty course."""
    course = Course(
        owner_id=current_user.id,
        title=course_in.title,
        description=course_in.description,
        difficulty=course_in.difficulty,
        language=course_in.language,
        is_public=course_in.is_public,
        tags=course_in.tags,
        status="ready",  # Without AI, course is immediately ready
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get a specific course by ID."""
    stmt = select(Course).where(
        Course.id == course_id,
        Course.owner_id == current_user.id,
        Course.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    return course


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: uuid.UUID,
    course_in: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Update a course."""
    stmt = select(Course).where(
        Course.id == course_id,
        Course.owner_id == current_user.id,
        Course.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    update_data = course_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
        
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_course(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Soft delete a course."""
    stmt = select(Course).where(
        Course.id == course_id,
        Course.owner_id == current_user.id,
        Course.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    from datetime import datetime, timezone
    course.deleted_at = datetime.now(timezone.utc)
    
    db.add(course)
    await db.commit()


@router.post("/{course_id}/generate", response_model=CourseResponse)
@limiter.limit("10/hour", key_func=_get_user_or_ip)
async def start_course_generation(
    request: Request,
    response: Response,
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Start the asynchronous course generation pipeline."""
    stmt = select(Course).where(
        Course.id == course_id,
        Course.owner_id == current_user.id,
        Course.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    if course.status in ["generating_outline", "generating_lessons"]:
        raise HTTPException(status_code=400, detail="Course is already generating")
        
    course.status = "generating_outline"
    course.generation_error = None
    db.add(course)
    await db.commit()
    await db.refresh(course)
    
    from tasks.generate_course_task import generate_course_task
    generate_course_task.delay(str(course.id))
    
    return course

@router.get("/{course_id}/structure")
async def get_course_structure(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get the full nested course structure (Lessons -> Topics -> Subtopics)."""
    from sqlalchemy.orm import selectinload
    
    stmt = select(Course).where(
        Course.id == course_id,
        Course.owner_id == current_user.id,
        Course.deleted_at.is_(None)
    ).options(
        selectinload(Course.lessons).selectinload(Lesson.topics).selectinload(Topic.subtopics)
    )
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Build a nested dictionary representation
    structure = []
    
    sorted_lessons = sorted(course.lessons, key=lambda x: x.order_index)
    for lesson in sorted_lessons:
        lesson_data = {
            "id": lesson.id,
            "title": lesson.title,
            "summary": lesson.summary,
            "status": lesson.status,
            "order_index": lesson.order_index,
            "topics": []
        }
        
        sorted_topics = sorted(lesson.topics, key=lambda x: x.order_index)
        for topic in sorted_topics:
            topic_data = {
                "id": topic.id,
                "title": topic.title,
                "content": topic.content,
                "order_index": topic.order_index,
                "subtopics": []
            }
            
            sorted_subtopics = sorted(topic.subtopics, key=lambda x: x.order_index)
            for subtopic in sorted_subtopics:
                topic_data["subtopics"].append({
                    "id": subtopic.id,
                    "title": subtopic.title,
                    "content": subtopic.content,
                    "order_index": subtopic.order_index
                })
                
            lesson_data["topics"].append(topic_data)
            
        structure.append(lesson_data)
        
    return {"course_id": course.id, "lessons": structure}
