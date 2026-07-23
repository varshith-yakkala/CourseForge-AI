"""Course request/response Pydantic schemas."""
from datetime import datetime
import uuid
from pydantic import BaseModel, Field, ConfigDict


class CourseBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500, description="The title of the course")
    description: str | None = Field(default=None, description="Detailed description of the course")
    difficulty: str | None = Field(default=None, description="Course difficulty (e.g. beginner, advanced)")
    language: str = Field(default="en", description="Primary language of the course")
    is_public: bool = Field(default=False, description="Whether the course is publicly visible")
    tags: list[str] | None = Field(default=None, description="List of tags or categories")


class CourseCreate(CourseBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Introduction to Machine Learning",
                "description": "Learn the basics of ML",
                "difficulty": "beginner",
                "language": "en",
                "is_public": False,
                "tags": ["AI", "Machine Learning"]
            }
        }
    )


class CourseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500, description="Updated title")
    description: str | None = Field(default=None, description="Updated description")
    difficulty: str | None = Field(default=None, description="Updated difficulty")
    is_public: bool | None = Field(default=None, description="Updated visibility")
    tags: list[str] | None = Field(default=None, description="Updated tags")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Advanced Machine Learning",
                "difficulty": "advanced"
            }
        }
    )


class CourseResponse(CourseBase):
    id: uuid.UUID = Field(..., description="Unique course identifier")
    owner_id: uuid.UUID = Field(..., description="User ID of the course creator")
    status: str = Field(..., description="Current status of the course (e.g. 'ready', 'generating')")
    thumbnail_url: str | None = Field(default=None, description="URL for the course thumbnail")
    estimated_duration_min: int | None = Field(default=None, description="Estimated duration in minutes")
    generation_error: str | None = Field(default=None, description="Error message if generation failed")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "c9a4e9b6-1234-5678-abcd-e89b12d3a456",
                "title": "Introduction to Machine Learning",
                "status": "ready",
                "created_at": "2026-07-23T00:00:00Z",
                "updated_at": "2026-07-23T00:00:00Z"
            }
        }
    )
