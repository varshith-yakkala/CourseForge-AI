from pydantic import BaseModel
import uuid
from datetime import datetime

class CoachAdviceResponse(BaseModel):
    tip: str
    coach_name: str
    avatar_icon: str
    previous_message: str | None = None

class HeatmapItemSchema(BaseModel):
    date: str
    count: int
    intensity: int

class HabitStatsResponse(BaseModel):
    course_id: str
    learning_streak_days: int
    longest_streak_days: int
    productivity_score: float
    consistency_score: float
    most_productive_time: str
    most_productive_day: str
    avg_session_mins: int
    habit_insights: list[str]
    heatmap_data: list[HeatmapItemSchema]

class NotificationResponse(BaseModel):
    id: uuid.UUID
    type: str
    priority: str
    title: str
    body: str | None = None
    is_read: bool
    link: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
