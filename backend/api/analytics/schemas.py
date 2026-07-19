from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class WeakTopicItem(BaseModel):
    lesson_id: str
    title: str
    score_pct: float

class StrongTopicItem(BaseModel):
    lesson_id: str
    title: str
    score_pct: float

class CourseAnalyticsResponse(BaseModel):
    course_id: str
    overall_progress_pct: float
    completed_lessons: int
    total_lessons: int
    total_time_spent_min: float
    avg_quiz_score: float
    passed_quizzes: int
    total_quizzes: int
    flashcard_retention_pct: float
    mastered_flashcards: int
    total_flashcards: int
    learning_streak_days: int
    weak_topics: list[WeakTopicItem]
    strong_topics: list[StrongTopicItem]

class RevisionRecommendationResponse(BaseModel):
    type: str
    priority: str
    title: str
    reason: str
    action_url: str

class UserAchievementResponse(BaseModel):
    id: uuid.UUID
    badge_key: str
    title: str
    description: str
    icon_name: str
    unlocked_at: datetime

    class Config:
        from_attributes = True

class ExportSummaryResponse(BaseModel):
    markdown_content: str
