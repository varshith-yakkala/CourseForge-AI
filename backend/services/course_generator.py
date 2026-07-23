"""
CourseForge AI - Course Generator Service
Responsibility: Generate complete course structure from an indexed PDF.
"""
from __future__ import annotations
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.course import Course
from db.models.lesson import Lesson
from db.models.topic import Topic
from db.models.subtopic import Subtopic
from db.models.document import Document
from llm.prompt_manager import PromptManager
from llm.schemas import CourseBlueprintResponse
from insightforge.engine import InsightForgeEngine
from core.exceptions import CourseForgeError

logger = logging.getLogger(__name__)

class CourseGeneratorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.engine = InsightForgeEngine()
        
    async def generate_blueprint(self, course_id: str) -> dict:
        """Generate the Course Blueprint (Layer 1)."""
        # Fetch Course and Document
        stmt = select(Course).where(Course.id == course_id)
        result = await self.db.execute(stmt)
        course = result.scalar_one_or_none()
        
        if not course:
            raise CourseForgeError("Course not found")
            
        stmt_doc = select(Document).where(Document.course_id == course_id)
        result_doc = await self.db.execute(stmt_doc)
        document = result_doc.scalar_one_or_none()
        
        if not document or document.index_status != "ready":
            raise CourseForgeError("Document not found or not ready")

        from core.progress import ProgressTracker
        import time

        t_llm_start = time.perf_counter()
        ProgressTracker.set_stage(course_id, "generating_course_blueprint", 70, "Generating course blueprint via Groq LLM")

        # 1. Retrieve chunks to form context
        chunks = self.engine.retrieve_chunks(
            query="Summarize the core concepts, outline, and main topics of this document to form a course syllabus.",
            doc_ids=[document.insightforge_doc_id],
            top_k=15
        )
        
        context = "\n".join([c.content for c in chunks])
        
        # 2. Build Prompt
        schema_json = CourseBlueprintResponse.model_json_schema()
        prompt = PromptManager.build(
            "course_blueprint", 
            document_context=context,
            schema=json.dumps(schema_json, indent=2)
        )
        
        # 3. Query LLM
        query_result = self.engine.query(
            question="Generate course blueprint", 
            doc_ids=[document.insightforge_doc_id],
            prompt_override=prompt
        )
        
        t_llm = round((time.perf_counter() - t_llm_start) * 1000, 2)
        ProgressTracker.record_timing(course_id, "llm_generation_ms", t_llm)

        answer = query_result.answer
        if not answer:
            raise CourseForgeError("LLM failed to generate a response.")
            
        # Parse and Validate with Pydantic
        try:
            # Sometime LLMs wrap json in ```json ... ```
            if "```json" in answer:
                answer = answer.split("```json")[1].split("```")[0]
            elif "```" in answer:
                answer = answer.split("```")[1].split("```")[0]
                
            data = json.loads(answer.strip())
            blueprint = CourseBlueprintResponse(**data)
        except Exception as e:
            logger.error(f"Failed to parse LLM blueprint response: {answer}")
            raise CourseForgeError(f"Blueprint parsing failed: {e}")

        # 4. Save to DB
        ProgressTracker.set_stage(course_id, "saving_course", 90, "Saving course syllabus and lessons to database")
        t_db_start = time.perf_counter()
        course.title = blueprint.title
        course.description = blueprint.description
        course.difficulty = blueprint.difficulty
        course.estimated_duration_min = blueprint.estimated_duration_min
        course.tags = blueprint.tags
        course.status = "ready"

        
        # Delete existing lessons if this is a regeneration
        import uuid
        from sqlalchemy import delete
        await self.db.execute(delete(Lesson).where(Lesson.course_id == course.id))
        
        objects_to_add = []
        for l_idx, l_data in enumerate(blueprint.lessons):
            lesson_id = uuid.uuid4()
            lesson = Lesson(
                id=lesson_id,
                course_id=course.id,
                title=l_data.title,
                summary=l_data.summary,
                order_index=l_idx,
                estimated_duration_min=l_data.estimated_duration_min,
                status="pending"
            )
            objects_to_add.append(lesson)
            
            for t_idx, t_data in enumerate(l_data.topics):
                topic_id = uuid.uuid4()
                topic = Topic(
                    id=topic_id,
                    lesson_id=lesson_id,
                    course_id=course.id,
                    title=t_data.title,
                    content=t_data.description,
                    order_index=t_idx,
                    key_terms=t_data.key_terms
                )
                objects_to_add.append(topic)
                
                for st_idx, st_data in enumerate(t_data.subtopics):
                    subtopic = Subtopic(
                        id=uuid.uuid4(),
                        topic_id=topic_id,
                        lesson_id=lesson_id,
                        course_id=course.id,
                        title=st_data.title,
                        content=st_data.description,
                        order_index=st_idx
                    )
                    objects_to_add.append(subtopic)
        self.db.add_all(objects_to_add)
        await self.db.commit()

        t_db = round((time.perf_counter() - t_db_start) * 1000, 2)
        ProgressTracker.record_timing(course_id, "db_write_ms", t_db)
        ProgressTracker.set_stage(course_id, "completed", 100, "Course generated successfully")
        return {"status": "success", "course_id": course_id}


