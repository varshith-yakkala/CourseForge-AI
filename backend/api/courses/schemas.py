"""Course request/response Pydantic schemas."""
from datetime import datetime
import uuid
from pydantic import BaseModel, Field


class CourseBase(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    difficulty: str | None = None
    language: str = "en"
    is_public: bool = False
    tags: list[str] | None = None


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    difficulty: str | None = None
    is_public: bool | None = None
    tags: list[str] | None = None


class CourseResponse(CourseBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    status: str
    thumbnail_url: str | None = None
    estimated_duration_min: int | None = None
    generation_error: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
