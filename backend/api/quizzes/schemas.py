from pydantic import BaseModel, Field
import uuid

class QuizQuestionResponse(BaseModel):
    id: uuid.UUID
    question_text: str
    question_type: str
    options: list[str] | None = None
    difficulty: str | None = None
    order_index: int

    class Config:
        from_attributes = True

class QuizRunnerResponse(BaseModel):
    quiz_id: uuid.UUID
    title: str
    pass_score_pct: float
    time_limit_min: int | None = 10
    questions: list[QuizQuestionResponse]

class SubmitQuizRequest(BaseModel):
    answers: dict[str, str] = Field(description="Map of question_id to user_answer string")
    difficulty: str = Field(default="Intermediate")
    time_taken_sec: int = Field(default=60)

class QuizQuestionBreakdown(BaseModel):
    question_id: str
    question_text: str
    question_type: str
    options: list[str] | None = None
    user_answer: str | None = None
    correct_answer: str
    is_correct: bool
    points_earned: float
    explanation: str | None = None

class SubmitQuizResponse(BaseModel):
    attempt_id: str
    quiz_id: str
    score_pct: float
    passed: bool
    total_questions: int
    correct_count: int
    time_taken_sec: int
    attempt_number: int
    breakdown: list[QuizQuestionBreakdown]
