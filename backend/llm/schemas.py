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


class QuestionItemSchema(BaseModel):
    question_text: str = Field(description="The question prompt")
    question_type: str = Field(description="multiple_choice, true_false, fill_blank, short_answer, code_output")
    options: list[str] | None = Field(default=None, description="Array of options for multiple choice or true/false")
    correct_answer: str = Field(description="The correct answer text or option label")
    explanation: str = Field(description="Detailed explanation of why the answer is correct")
    difficulty: str = Field(default="Intermediate", description="Beginner, Intermediate, or Advanced")


class QuizGenerationResponse(BaseModel):
    title: str = Field(description="Quiz Title")
    questions: list[QuestionItemSchema] = Field(description="List of generated questions in pool")


class FlashcardItemSchema(BaseModel):
    front: str = Field(description="Concept, vocabulary term, or question")
    back: str = Field(description="Definition, explanation, and practical example")


class FlashcardGenerationResponse(BaseModel):
    flashcards: list[FlashcardItemSchema] = Field(description="List of generated flashcards")


class DailyScheduleBlockSchema(BaseModel):
    day_name: str = Field(description="e.g. Day 1, Monday, etc.")
    title: str = Field(description="Title of study block or lesson")
    activity_type: str = Field(description="lesson, quiz, flashcards, revision")
    estimated_mins: int = Field(description="Duration in minutes")
    lesson_id: str | None = Field(default=None)


class StudyScheduleResponse(BaseModel):
    schedule_blocks: list[DailyScheduleBlockSchema] = Field(description="List of planned daily study blocks")
    estimated_completion_date: str = Field(description="ISO Date string or YYYY-MM-DD")
    on_time_probability_pct: float = Field(description="Probability percentage 0-100%")
    remaining_hours: float = Field(description="Total remaining hours")


