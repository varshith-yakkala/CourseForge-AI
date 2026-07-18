"""Pydantic schemas for validating LLM outputs."""
from pydantic import BaseModel, Field

class SubtopicOutline(BaseModel):
    title: str = Field(description="Title of the subtopic")
    description: str = Field(description="Brief summary of what this subtopic covers")

class TopicOutline(BaseModel):
    title: str = Field(description="Title of the topic")
    description: str = Field(description="Brief summary of what this topic covers")
    key_terms: list[str] = Field(description="Key vocabulary terms for this topic")
    subtopics: list[SubtopicOutline] = Field(description="List of subtopics")

class LessonOutline(BaseModel):
    title: str = Field(description="Title of the lesson")
    summary: str = Field(description="Summary of the lesson")
    estimated_duration_min: int = Field(description="Estimated time to complete this lesson in minutes")
    topics: list[TopicOutline] = Field(description="List of topics covered in this lesson")

class CourseBlueprintResponse(BaseModel):
    title: str = Field(description="The proposed title of the course")
    description: str = Field(description="A comprehensive overview of the course")
    difficulty: str = Field(description="Difficulty level: Beginner, Intermediate, or Advanced")
    learning_objectives: list[str] = Field(description="What the student will learn")
    estimated_duration_min: int = Field(description="Total estimated time in minutes")
    tags: list[str] = Field(description="5 relevant tags or keywords for the course")
    lessons: list[LessonOutline] = Field(description="List of lessons making up the course")
