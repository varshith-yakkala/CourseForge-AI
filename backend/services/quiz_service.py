"""
CourseForge AI — Quiz Service
Responsibility: Generate question pools, deliver randomized adaptive quizzes, score attempts with partial credit, and persist results.
"""
from __future__ import annotations

import json
import random
import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.quiz import Quiz
from db.models.quiz_question import QuizQuestion
from db.models.quiz_attempt import QuizAttempt
from db.models.quiz_attempt_answer import QuizAttemptAnswer
from db.models.lesson import Lesson
from db.models.course import Course
from db.models.document import Document
from llm.prompt_manager import PromptManager
from llm.schemas import QuizGenerationResponse
from insightforge.engine import InsightForgeEngine
from core.exceptions import CourseForgeError

logger = logging.getLogger(__name__)


class QuizService:
    """Service to manage adaptive quizzes, question pools, scoring, and attempts."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.engine = InsightForgeEngine()

    async def get_or_generate_quiz(
        self, course_id: str, lesson_id: str, difficulty: str = "Intermediate", force: bool = False
    ) -> Quiz:
        """
        Fetch or on-demand generate the Quiz and Question Pool for a lesson.
        """
        # Fetch Quiz if exists
        stmt_quiz = select(Quiz).where(Quiz.lesson_id == lesson_id)
        res_quiz = await self.db.execute(stmt_quiz)
        quiz = res_quiz.scalar_one_or_none()

        if quiz and not force:
            # Check if questions exist
            stmt_q = select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id)
            res_q = await self.db.execute(stmt_q)
            questions = res_q.scalars().all()
            if questions:
                return quiz

        # Fetch Lesson & Document context for quiz generation
        stmt_lesson = select(Lesson).where(Lesson.id == lesson_id)
        res_lesson = await self.db.execute(stmt_lesson)
        lesson = res_lesson.scalar_one_or_none()

        if not lesson:
            raise CourseForgeError("Lesson not found", status_code=404)

        stmt_doc = select(Document).where(Document.course_id == course_id)
        res_doc = await self.db.execute(stmt_doc)
        document = res_doc.scalar_one_or_none()

        document_context = ""
        if document and document.index_status == "ready" and document.insightforge_doc_id:
            try:
                chunks = self.engine.retrieve_chunks(
                    query=f"{lesson.title} key concepts quiz questions",
                    doc_ids=[document.insightforge_doc_id],
                    top_k=8,
                )
                document_context = "\n\n".join([c.content for c in chunks])
            except Exception as exc:
                logger.warning(f"Could not retrieve chunks for quiz generation: {exc}")

        # Build prompt
        schema_json = QuizGenerationResponse.model_json_schema()
        prompt = PromptManager.build(
            "quiz_generation",
            version="v1",
            lesson_title=lesson.title,
            lesson_markdown=lesson.content_markdown or lesson.summary or lesson.title,
            document_context=document_context or "Standard lesson topic context.",
            difficulty=difficulty,
            schema=json.dumps(schema_json, indent=2),
        )

        query_res = self.engine.query(
            question=f"Generate quiz pool for {lesson.title}",
            doc_ids=[document.insightforge_doc_id] if (document and document.insightforge_doc_id) else [],
            prompt_override=prompt,
        )

        answer = query_res.answer
        if not answer:
            raise CourseForgeError("LLM failed to generate quiz response", status_code=500)

        # Parse JSON
        try:
            cleaned = answer.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0]
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0]
            
            data = json.loads(cleaned.strip())
            quiz_resp = QuizGenerationResponse(**data)
        except Exception as exc:
            logger.error(f"Failed to parse quiz response: {answer}")
            raise CourseForgeError(f"Quiz parsing error: {exc}", status_code=500)

        # Create or update Quiz DB record
        if not quiz:
            quiz = Quiz(
                course_id=course_id,
                lesson_id=lesson_id,
                title=f"Quiz: {lesson.title}",
                pass_score_pct=70.0,
                time_limit_min=10,
            )
            self.db.add(quiz)
            await self.db.flush()
        else:
            # Delete old questions if regenerating
            from sqlalchemy import delete
            await self.db.execute(delete(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id))
            await self.db.flush()

        for idx, q_item in enumerate(quiz_resp.questions):
            qq = QuizQuestion(
                quiz_id=quiz.id,
                question_text=q_item.question_text,
                question_type=q_item.question_type or "multiple_choice",
                options=q_item.options,
                correct_answer=q_item.correct_answer,
                explanation=q_item.explanation,
                difficulty=q_item.difficulty or difficulty,
                order_index=idx,
            )
            self.db.add(qq)

        await self.db.commit()
        await self.db.refresh(quiz)
        return quiz

    async def get_quiz_questions(
        self, quiz_id: str, difficulty: str = "Intermediate", num_questions: int = 10
    ) -> list[QuizQuestion]:
        """
        Deliver a randomized subset (e.g. 10 questions) from the question pool for replayability.
        """
        stmt = select(QuizQuestion).where(QuizQuestion.quiz_id == quiz_id)
        res = await self.db.execute(stmt)
        questions = res.scalars().all()

        if not questions:
            return []

        # Filter or prioritize requested difficulty, fallback to full pool
        filtered = [q for q in questions if q.difficulty == difficulty]
        pool = filtered if len(filtered) >= 5 else questions

        sample_size = min(len(pool), num_questions)
        sampled = random.sample(pool, sample_size)
        return sampled

    async def submit_attempt(
        self,
        quiz_id: str,
        user_id: str,
        user_answers: dict[str, str], # question_id -> answer_string
        difficulty: str = "Intermediate",
        time_taken_sec: int = 60,
    ) -> dict:
        """
        Score attempt with partial credit support for short answer / scenario questions.
        Save QuizAttempt and QuizAttemptAnswer DB records.
        """
        stmt_quiz = select(Quiz).where(Quiz.id == quiz_id)
        res_quiz = await self.db.execute(stmt_quiz)
        quiz = res_quiz.scalar_one_or_none()

        if not quiz:
            raise CourseForgeError("Quiz not found", status_code=404)

        # Count previous attempts
        stmt_prev = select(QuizAttempt).where(QuizAttempt.quiz_id == quiz_id, QuizAttempt.user_id == user_id)
        res_prev = await self.db.execute(stmt_prev)
        prev_attempts = res_prev.scalars().all()
        attempt_number = len(prev_attempts) + 1

        now = datetime.now(timezone.utc)
        attempt = QuizAttempt(
            quiz_id=quiz.id,
            user_id=user_id,
            started_at=now,
            submitted_at=now,
            attempt_number=attempt_number,
            time_taken_sec=time_taken_sec,
        )
        self.db.add(attempt)
        await self.db.flush()

        total_questions = len(user_answers)
        if total_questions == 0:
            total_questions = 1

        correct_count = 0
        earned_score_pts = 0.0
        breakdown = []

        for q_id_str, user_ans in user_answers.items():
            stmt_q = select(QuizQuestion).where(QuizQuestion.id == q_id_str)
            res_q = await self.db.execute(stmt_q)
            q_obj = res_q.scalar_one_or_none()

            if not q_obj:
                continue

            is_correct = False
            points = 0.0
            clean_user = (user_ans or "").strip().lower()
            clean_correct = (q_obj.correct_answer or "").strip().lower()

            if q_obj.question_type in ("multiple_choice", "true_false"):
                if clean_user == clean_correct:
                    is_correct = True
                    points = 1.0
            else:
                # Short answer / fill_blank / code_output: partial credit matching
                if clean_user == clean_correct:
                    is_correct = True
                    points = 1.0
                elif clean_correct in clean_user or clean_user in clean_correct:
                    is_correct = True
                    points = 0.8 # Partial credit
                else:
                    points = 0.0

            earned_score_pts += points
            if is_correct:
                correct_count += 1

            # Save answer
            ans_record = QuizAttemptAnswer(
                attempt_id=attempt.id,
                question_id=q_obj.id,
                user_answer=user_ans,
                is_correct=is_correct,
            )
            self.db.add(ans_record)

            breakdown.append({
                "question_id": str(q_obj.id),
                "question_text": q_obj.question_text,
                "question_type": q_obj.question_type,
                "options": q_obj.options,
                "user_answer": user_ans,
                "correct_answer": q_obj.correct_answer,
                "is_correct": is_correct,
                "points_earned": points,
                "explanation": q_obj.explanation,
            })

        score_pct = round((earned_score_pts / total_questions) * 100, 2)
        passed = score_pct >= float(quiz.pass_score_pct)

        attempt.score_pct = score_pct
        attempt.passed = passed

        self.db.add(attempt)
        await self.db.commit()

        return {
            "attempt_id": str(attempt.id),
            "quiz_id": str(quiz.id),
            "score_pct": score_pct,
            "passed": passed,
            "total_questions": total_questions,
            "correct_count": correct_count,
            "time_taken_sec": time_taken_sec,
            "attempt_number": attempt_number,
            "breakdown": breakdown,
        }
