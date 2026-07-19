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

        # 1. Fetch Lesson
        stmt_lesson = select(Lesson).where(
            Lesson.id == lesson_id, Lesson.course_id == course_id
        )
        res_lesson = await self.db.execute(stmt_lesson)
        lesson = res_lesson.scalar_one_or_none()

        if not lesson:
            raise CourseForgeError(detail="Lesson not found", status_code=404)

        if not lesson.content_markdown:
            raise CourseForgeError(
                detail="Lesson content has not been generated yet. Please generate the lesson first.",
                status_code=400,
            )

        # 2. Fetch Document RAG Context
        stmt_doc = select(Document).where(Document.course_id == course_id)
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
        prompt = PromptManager.build(
            "lesson_tutor",
            version="v1",
            lesson_markdown=lesson.content_markdown[:6000], # Pass main lesson content
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
