import pytest
from unittest.mock import AsyncMock, MagicMock
import uuid

@pytest.mark.asyncio
async def test_get_or_generate_quiz_cached(mocker):
    from services.quiz_service import QuizService

    mock_db = AsyncMock()

    mock_quiz = type("Quiz", (), {
        "id": "q1",
        "course_id": "c1",
        "lesson_id": "l1",
        "title": "Quiz 1",
        "pass_score_pct": 70.0,
    })()

    mock_q = type("QuizQuestion", (), {
        "id": "qq1",
        "quiz_id": "q1",
        "question_text": "What is Python?",
        "question_type": "multiple_choice",
        "difficulty": "Intermediate",
    })()

    mock_res_quiz = MagicMock()
    mock_res_quiz.scalar_one_or_none.return_value = mock_quiz

    mock_res_q = MagicMock()
    mock_res_q.scalars.return_value.all.return_value = [mock_q]

    mock_db.execute.side_effect = [mock_res_quiz, mock_res_q]
    mocker.patch("services.quiz_service.InsightForgeEngine")

    service = QuizService(mock_db)
    res = await service.get_or_generate_quiz("c1", "l1", force=False)

    assert res.id == "q1"


@pytest.mark.asyncio
async def test_submit_attempt_scoring(mocker):
    from services.quiz_service import QuizService

    mock_db = AsyncMock()
    q_id = uuid.uuid4()
    u_id = uuid.uuid4()
    qq_id = uuid.uuid4()

    mock_quiz = type("Quiz", (), {
        "id": q_id,
        "pass_score_pct": 70.0,
    })()

    mock_question = type("QuizQuestion", (), {
        "id": qq_id,
        "question_text": "Is Python interpreted?",
        "question_type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "True",
        "explanation": "Yes, Python is an interpreted language.",
    })()

    mock_res_quiz = MagicMock()
    mock_res_quiz.scalar_one_or_none.return_value = mock_quiz

    mock_res_prev = MagicMock()
    mock_res_prev.scalars.return_value.all.return_value = []

    mock_res_q = MagicMock()
    mock_res_q.scalar_one_or_none.return_value = mock_question

    mock_db.execute.side_effect = [mock_res_quiz, mock_res_prev, mock_res_q]
    mocker.patch("services.quiz_service.InsightForgeEngine")

    service = QuizService(mock_db)
    res = await service.submit_attempt(
        quiz_id=str(q_id),
        user_id=str(u_id),
        user_answers={str(qq_id): "True"},
    )

    assert res["passed"] is True
    assert res["score_pct"] == 100.0
    assert res["correct_count"] == 1
