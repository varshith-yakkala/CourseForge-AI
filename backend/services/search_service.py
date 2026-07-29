import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models.course import Course
from db.models.document import Document
from db.models.lesson import Lesson
from insightforge.engine import InsightForgeEngine, ChunkResult
from core.exceptions import CourseForgeError

logger = logging.getLogger(__name__)

class SearchService:
    """Unified AI-synthesized search with multi-step reasoning, citations, and collapsible sources."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.engine = InsightForgeEngine()

    async def ai_search(
        self,
        query: str,
        user_id: str,
        course_id: str | None = None,
        persona: str = "intermediate", # beginner, intermediate, expert, interview, exam
        style: str = "detailed", # shorter, deeper, examples, analogies
        top_k: int = 8,
    ) -> dict:
        import uuid
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id

        stmt = select(Document, Course).join(Course, Document.course_id == Course.id).where(
            Course.owner_id == user_uuid,
            Document.index_status == "ready"
        )

        course_title = "All Courses"
        if course_id:
            try:
                course_uuid = uuid.UUID(course_id) if isinstance(course_id, str) else course_id
                stmt = stmt.where(Course.id == course_uuid)
            except ValueError:
                pass

        res = await self.db.execute(stmt)
        rows = res.all()
        if not rows:
            return {
                "answer": "No indexed document content found for this search.",
                "summary": "No documents available.",
                "explanation": "Please upload a PDF document first to perform AI search.",
                "key_points": [],
                "confidence": 0.0,
                "relevant_lesson": None,
                "retrieved_sources": [],
            }

        valid_doc_ids = [doc.insightforge_doc_id for doc, c in rows if doc.insightforge_doc_id]
        if rows:
            course_title = rows[0][1].title

        # Step 1: Hybrid Retrieval (FAISS + BM25)
        import asyncio
        chunks: list[ChunkResult] = await asyncio.to_thread(
            self.engine.retrieve_chunks,
            query,
            valid_doc_ids,
            top_k
        )

        if not chunks:
            return {
                "answer": "No relevant evidence found in the document store for your question.",
                "summary": "No matching context found.",
                "explanation": "Try rephrasing your search query.",
                "key_points": [],
                "confidence": 0.1,
                "relevant_lesson": None,
                "retrieved_sources": [],
            }

        # Format retrieved chunks context
        formatted_context = []
        retrieved_sources = []
        for idx, c in enumerate(chunks, 1):
            doc_name = getattr(c, "file_name", "Document") or "Document"
            page_str = f"Page {c.page}" if c.page else "Unknown Page"
            formatted_context.append(f"[{idx}] {doc_name} ({page_str}) [Score: {c.score:.2f}]:\n{c.content}")
            retrieved_sources.append({
                "source_id": str(idx),
                "chunk_id": c.chunk_id,
                "document_id": c.document_id,
                "file_name": doc_name,
                "page": c.page,
                "similarity_score": round(c.score, 3),
                "snippet": c.content[:300] + ("..." if len(c.content) > 300 else ""),
                "full_content": c.content,
            })

        context_str = "\n\n".join(formatted_context)

        # Step 2: Retrieve relevant lesson match from DB
        stmt_lessons = select(Lesson).join(Course, Lesson.course_id == Course.id).where(Course.owner_id == user_uuid)
        if course_id:
            stmt_lessons = stmt_lessons.where(Lesson.course_id == course_uuid)
        res_l = await self.db.execute(stmt_lessons)
        lessons = res_l.scalars().all()
        relevant_lesson = None
        for l in lessons:
            if any(term.lower() in l.title.lower() for term in query.split() if len(term) > 3):
                relevant_lesson = {"id": str(l.id), "title": l.title}
                break
        if not relevant_lesson and lessons:
            relevant_lesson = {"id": str(lessons[0].id), "title": lessons[0].title}

        # Step 3: LLM Synthesized Multi-step Reasoning
        prompt = (
            f"You are CourseForge AI Master Assistant. Answer the user question based STRICTLY on the retrieved context below.\n\n"
            f"USER QUESTION: {query}\n"
            f"TARGET PERSONA: {persona} level\n"
            f"ANSWER STYLE: {style}\n\n"
            f"RETRIEVED CONTEXT:\n{context_str}\n\n"
            f'{{\n'
            f'  "summary": "1-2 sentence direct answer summary",\n'
            f'  "explanation": "Detailed step-by-step breakdown",\n'
            f'  "key_points": ["bullet 1", "bullet 2", "bullet 3"],\n'
            f'  "confidence": 0.95,\n'
            f'  "citations": [{{"pdf_name": "filename.pdf", "page": 1, "score": 0.85}}]\n'
            f'}}\n'
            f"Do not hallucinate facts outside the provided context. If evidence is missing, state it clearly."

        )

        query_res = await asyncio.to_thread(
            self.engine.query,
            query,
            valid_doc_ids,
            prompt
        )

        answer_text = query_res.answer or ""
        summary = "AI answer synthesized successfully."
        explanation = answer_text
        key_points = []
        confidence = 0.85

        try:
            cleaned = answer_text.strip()
            if "```json" in cleaned:
                cleaned = cleaned.split("```json")[1].split("```")[0]
            elif "```" in cleaned:
                cleaned = cleaned.split("```")[1].split("```")[0]
            parsed = json.loads(cleaned.strip())
            summary = parsed.get("summary", summary)
            explanation = parsed.get("explanation", explanation)
            key_points = parsed.get("key_points", key_points)
            confidence = parsed.get("confidence", confidence)
        except Exception:
            pass

        return {
            "answer": answer_text,
            "summary": summary,
            "explanation": explanation,
            "key_points": key_points,
            "confidence": confidence,
            "relevant_lesson": relevant_lesson,
            "retrieved_sources": retrieved_sources,
        }
