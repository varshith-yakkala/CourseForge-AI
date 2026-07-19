from pydantic import BaseModel, Field
import uuid
from datetime import datetime

class FlashcardResponse(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    lesson_id: uuid.UUID | None = None
    front: str
    back: str
    order_index: int

    class Config:
        from_attributes = True

class ReviewFlashcardRequest(BaseModel):
    rating: str = Field(description="again, hard, good, easy")

class ReviewFlashcardResponse(BaseModel):
    id: uuid.UUID
    flashcard_id: uuid.UUID
    rating: str
    interval_days: int
    ease_factor: float
    next_review_at: datetime
    reviewed_at: datetime

    class Config:
        from_attributes = True
