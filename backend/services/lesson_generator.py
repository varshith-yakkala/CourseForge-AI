"""
CourseForge AI — Lesson Generator Service
Responsibility: Generate detailed Markdown lesson content on-demand using InsightForge RAG context.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.course import Course
from db.models.lesson import Lesson
from db.models.topic import Topic
from db.models.document import Document
from llm.prompt_manager import PromptManager
from insightforge.engine import InsightForgeEngine
from core.exceptions import CourseForgeError

logger = logging.getLogger(__name__)


class LessonGeneratorService:
    """Service to handle on-demand lesson content generation and caching."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.engine = InsightForgeEngine()

    async def generate_lesson(
        self, course_id: str, lesson_id: str, force_regenerate: bool = False
    ) -> Lesson:
        """
        Generate or fetch cached lesson content.
        
        Lifecycle: PENDING / FAILED / READY ➔ GENERATING ➔ READY or FAILED
        """
        # 1. Fetch Lesson
        stmt_lesson = select(Lesson).where(
            Lesson.id == lesson_id, Lesson.course_id == course_id
        )
        res_lesson = await self.db.execute(stmt_lesson)
        lesson = res_lesson.scalar_one_or_none()

        if not lesson:
            raise CourseForgeError(detail="Lesson not found", status_code=404)

        # 2. Return cached lesson if already generated and not forced
        if not force_regenerate and lesson.status == "ready" and lesson.content_markdown:
            logger.info(f"Returning cached lesson content for lesson {lesson_id} (v{lesson.version})")
            return lesson

        # 3. Fetch Course and Document
        stmt_course = select(Course).where(Course.id == course_id)
        res_course = await self.db.execute(stmt_course)
        course = res_course.scalar_one_or_none()

        if not course:
            raise CourseForgeError(detail="Course not found", status_code=404)

        stmt_doc = select(Document).where(Document.course_id == course_id)
        res_doc = await self.db.execute(stmt_doc)
        document = res_doc.scalar_one_or_none()

        # Fetch Topics for this lesson
        stmt_topics = select(Topic).where(Topic.lesson_id == lesson_id).order_by(Topic.order_index)
        res_topics = await self.db.execute(stmt_topics)
        topics = res_topics.scalars().all()

        topics_summary_str = "\n".join([f"- {t.title}: {t.content}" for t in topics]) if topics else lesson.summary or lesson.title

        # Update status to GENERATING
        lesson.status = "generating"
        lesson.generation_error = None
        self.db.add(lesson)
        await self.db.commit()
        await self.db.refresh(lesson)

        try:
            document_context = ""
            if document and document.index_status == "ready" and document.insightforge_doc_id:
                # Retrieve relevant RAG context from InsightForge
                search_query = f"{lesson.title} {lesson.summary or ''} {topics_summary_str}"
                chunks = self.engine.retrieve_chunks(
                    query=search_query,
                    doc_ids=[document.insightforge_doc_id],
                    top_k=10
                )
                document_context = "\n\n".join([c.content for c in chunks])
            
            if not document_context:
                document_context = f"Lesson topic: {lesson.title}. Summary: {lesson.summary or 'N/A'}"

            # Build prompt
            prompt = PromptManager.build(
                "lesson_content",
                version="v1",
                lesson_title=lesson.title,
                lesson_summary=lesson.summary or lesson.title,
                course_title=course.title,
                topics_summary=topics_summary_str,
                document_context=document_context,
                estimated_duration=lesson.estimated_duration_min or 15,
            )

            # Query LLM
            query_result = self.engine.query(
                question=f"Generate lesson: {lesson.title}",
                doc_ids=[document.insightforge_doc_id] if (document and document.insightforge_doc_id) else [],
                prompt_override=prompt
            )

            markdown_text = query_result.answer
            if not markdown_text:
                raise CourseForgeError("LLM returned empty response for lesson generation")

            # Clean markdown code blocks wrappers if LLM accidentally wrapped full output
            cleaned_md = markdown_text.strip()
            if cleaned_md.startswith("```markdown"):
                cleaned_md = cleaned_md[11:]
                if cleaned_md.endswith("```"):
                    cleaned_md = cleaned_md[:-3]
            elif cleaned_md.startswith("```"):
                cleaned_md = cleaned_md[3:]
                if cleaned_md.endswith("```"):
                    cleaned_md = cleaned_md[:-3]
            cleaned_md = cleaned_md.strip()

            # Increment version if regenerating
            if force_regenerate and lesson.content_markdown:
                lesson.version += 1

            lesson.content_markdown = cleaned_md
            lesson.status = "ready"
            lesson.generated_at = datetime.now(timezone.utc)
            lesson.generation_error = None
            lesson.llm_metadata = json.dumps({
                "model": getattr(query_result, "model", "llama-3.3-70b-versatile"),
                "chunks_used": 10 if document_context else 0,
                "version": lesson.version,
            })

            self.db.add(lesson)
            await self.db.commit()
            await self.db.refresh(lesson)

            logger.info(f"Successfully generated lesson {lesson_id} (version {lesson.version})")
            return lesson

        except Exception as exc:
            logger.error(f"Failed to generate lesson {lesson_id}: {exc}")
            lesson.status = "failed"
            lesson.generation_error = str(exc)
            self.db.add(lesson)
            await self.db.commit()
            await self.db.refresh(lesson)
            raise CourseForgeError(detail=f"Lesson generation failed: {exc}", status_code=500)
