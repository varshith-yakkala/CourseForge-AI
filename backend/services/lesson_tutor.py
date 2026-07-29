"""
CourseForge AI — Lesson Tutor Service
Responsibility: Scoped AI Assistant to answer questions about the active lesson.
"""
from __future__ import annotations

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.lesson import Lesson
from db.models.document import Document
from llm.prompt_manager import PromptManager
from insightforge.engine import InsightForgeEngine
from core.exceptions import CourseForgeError

logger = logging.getLogger(__name__)


class LessonTutorService:
    """Service providing scoped AI tutoring on specific lessons."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.engine = InsightForgeEngine()

    async def ask_question(
        self, course_id: str, lesson_id: str, question: str
    ) -> dict[str, str]:
        """
        Answer a question scoped strictly to the current lesson's Markdown content and RAG context.
        """
        if not question or not question.strip():
            raise CourseForgeError(detail="Question cannot be empty", status_code=400)

        import uuid
        try:
            course_uuid = uuid.UUID(course_id) if isinstance(course_id, str) else course_id
        except ValueError:
            course_uuid = course_id
        try:
            lesson_uuid = uuid.UUID(lesson_id) if isinstance(lesson_id, str) else lesson_id
        except ValueError:
            lesson_uuid = lesson_id

        # 1. Fetch Lesson
        stmt_lesson = select(Lesson).where(
            Lesson.id == lesson_uuid, Lesson.course_id == course_uuid
        )
        res_lesson = await self.db.execute(stmt_lesson)
        lesson = res_lesson.scalar_one_or_none()

        if not lesson:
            raise CourseForgeError(detail="Lesson not found", status_code=404)

        if not lesson.content_markdown:
            from services.lesson_generator import LessonGeneratorService
            try:
                gen_service = LessonGeneratorService(self.db)
                lesson = await gen_service.generate_lesson(str(course_uuid), str(lesson_uuid), force_regenerate=False)
            except Exception as e:
                logger.warning("On-demand lesson content generation failed: %s", e)

        # 2. Fetch Document RAG Context
        stmt_doc = select(Document).where(Document.course_id == course_uuid)
        res_doc = await self.db.execute(stmt_doc)
        document = res_doc.scalar_one_or_none()

        document_context = ""
        if document and document.index_status == "ready" and document.insightforge_doc_id:
            try:
                chunks = self.engine.retrieve_chunks(
                    query=question,
                    doc_ids=[document.insightforge_doc_id],
                    top_k=5,
                )
                document_context = "\n\n".join([c.content for c in chunks])
            except Exception as e:
                logger.warning(f"Could not fetch RAG chunks for tutor question: {e}")

        # 3. Build Prompt
        lesson_text = (lesson.content_markdown or lesson.summary or lesson.title or "")[:6000]
        prompt = PromptManager.build(
            "lesson_tutor",
            version="v1",
            lesson_markdown=lesson_text, # Pass main lesson content
            document_context=document_context or "No extra document fragments.",
            question=question.strip(),
        )

        # 4. Query LLM
        query_result = self.engine.query(
            question=question,
            doc_ids=[document.insightforge_doc_id] if (document and document.insightforge_doc_id) else [],
            prompt_override=prompt,
        )

        answer = query_result.answer
        if not answer:
            raise CourseForgeError("AI tutor was unable to generate an answer.", status_code=500)

        return {"answer": answer.strip(), "lesson_id": str(lesson_id)}

    async def run_quick_action(self, course_id: str, lesson_id: str, action: str) -> dict[str, str]:
        """
        Run one of the 8 AI Study Assistant quick actions:
        summarize, eli5, examples, interview_questions, practice_questions, key_formulas, takeaways, common_mistakes
        """
        action_prompts = {
            "summarize": "Provide an executive summary of this lesson with core highlights.",
            "eli5": "Explain the core concept of this lesson like I am 10 years old, using simple language.",
            "examples": "Give 3 realistic, real-world practical examples illustrating the concepts in this lesson.",
            "interview_questions": "Generate 5 technical interview questions with answer guidelines based on this lesson.",
            "practice_questions": "Create 3 practice exercises with step-by-step solutions for this lesson.",
            "key_formulas": "Extract and explain all important formulas, equations, or key rules in this lesson.",
            "takeaways": "List the top 5 key takeaways and essential memory bullet points for this lesson.",
            "common_mistakes": "Detail 3 common pitfalls, misconceptions, or mistakes students make in this lesson and how to avoid them.",
        }

        prompt_question = action_prompts.get(action.lower(), f"Provide a detailed analysis for action: {action}")
        res = await self.ask_question(course_id, lesson_id, prompt_question)
        res["action"] = action
        return res

