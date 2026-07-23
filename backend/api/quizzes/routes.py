from fastapi import APIRouter, Depends, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from api.deps import get_db, get_current_user
from core.rate_limit import limiter, _get_user_or_ip
from db.models.user import User
from services.quiz_service import QuizService
from api.quizzes.schemas import QuizRunnerResponse, SubmitQuizRequest, SubmitQuizResponse

router = APIRouter(tags=["quizzes"])


@router.get("/courses/{course_id}/lessons/{lesson_id}/quiz", response_model=QuizRunnerResponse)
@limiter.limit("30/hour", key_func=_get_user_or_ip)
async def get_or_create_lesson_quiz(
    request: Request,
    response: Response,
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    difficulty: str = Query("Intermediate", description="Beginner, Intermediate, Advanced"),
    num_questions: int = Query(10, description="Number of questions to include in runner"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = QuizService(db)
    quiz = await service.get_or_generate_quiz(
        course_id=str(course_id),
        lesson_id=str(lesson_id),
        difficulty=difficulty,
    )
    questions = await service.get_quiz_questions(
        quiz_id=str(quiz.id),
        difficulty=difficulty,
        num_questions=num_questions,
    )

    return QuizRunnerResponse(
        quiz_id=quiz.id,
        title=quiz.title,
        pass_score_pct=float(quiz.pass_score_pct),
        time_limit_min=quiz.time_limit_min or 10,
        questions=questions,
    )


@router.post("/quizzes/{quiz_id}/submit", response_model=SubmitQuizResponse)
async def submit_quiz_attempt(
    quiz_id: uuid.UUID,
    req: SubmitQuizRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = QuizService(db)
    res = await service.submit_attempt(
        quiz_id=str(quiz_id),
        user_id=str(current_user.id),
        user_answers=req.answers,
        difficulty=req.difficulty,
        time_taken_sec=req.time_taken_sec,
    )
    return SubmitQuizResponse(**res)
