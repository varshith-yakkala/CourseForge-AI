"""Pydantic schemas for Lesson API routes."""
from datetime import datetime
import uuid
from pydantic import BaseModel, Field


class TopicResponse(BaseModel):
    id: uuid.UUID
    lesson_id: uuid.UUID
    course_id: uuid.UUID
    title: str
    content: str
    order_index: int
    key_terms: list[str] | None = None

    model_config = {"from_attributes": True}


class LessonDetailResponse(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    title: str
    summary: str | None = None
    status: str # pending, generating, ready, failed
    order_index: int
    estimated_duration_min: int | None = None
    content_markdown: str | None = None
    version: int = 1
    generated_at: datetime | None = None
    generation_error: str | None = None
    topics: list[TopicResponse] = []

    model_config = {"from_attributes": True}


class UpdateProgressRequest(BaseModel):
    status: str = Field(description="not_started, in_progress, completed")
    completed: bool = False
    completion_percentage: int = Field(default=0, ge=0, le=100)
    time_spent_sec: int = Field(default=0, ge=0)
    last_scroll_position: int | None = None


class ProgressResponse(BaseModel):
    user_id: uuid.UUID
    course_id: uuid.UUID
    lesson_id: uuid.UUID | None = None
    status: str
    completed: bool
    completion_percentage: int
    started_at: datetime | None = None
    completed_at: datetime | None = None
    last_opened_at: datetime | None = None
    last_scroll_position: int | None = None
    time_spent_sec: int = 0

    model_config = {"from_attributes": True}


class CourseProgressOverview(BaseModel):
    course_id: uuid.UUID
    total_lessons: int
    completed_lessons: int
    progress_percentage: int
    last_opened_lesson_id: uuid.UUID | None = None
    lessons_progress: list[ProgressResponse] = []


class AskTutorRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class AskTutorResponse(BaseModel):
    answer: str
    lesson_id: uuid.UUID
