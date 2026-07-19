from pydantic import BaseModel, Field
import uuid
from datetime import date

class StudyPlanRequest(BaseModel):
    daily_goal_min: int = Field(default=30, ge=5, le=300)
    target_completion_date: date | None = None
    preferred_study_days: list[str] | None = None

class ScheduleBlockResponse(BaseModel):
    day_name: str
    date: str
    title: str
    activity_type: str
    estimated_mins: int
    lesson_id: str | None = None

class AdaptiveScheduleResponse(BaseModel):
    daily_goal_min: int
    target_completion_date: str | None = None
    estimated_completion_date: str
    remaining_uncompleted_lessons: int
    remaining_hours: float
    schedule_blocks: list[ScheduleBlockResponse]

class CalendarEventResponse(BaseModel):
    id: str
    title: str
    date: str
    event_type: str
    status: str

class LearningPredictionsResponse(BaseModel):
    course_id: str
    estimated_completion_date: str
    on_time_probability_pct: float
    predicted_quiz_score_pct: float
    confidence_level: str
    remaining_lessons: int
