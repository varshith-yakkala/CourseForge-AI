"""Search routes."""
import logging
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.deps import get_current_active_user, get_db
from core.rate_limit import limiter, _get_user_or_ip
from pydantic import BaseModel
from db.models.user import User
from db.models.course import Course
from db.models.document import Document
from insightforge.engine import InsightForgeEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Search"])

class SearchRequest(BaseModel):
    query: str
    course_id: str | None = None
    top_k: int = 10

@router.post("")
@limiter.limit("30/hour", key_func=_get_user_or_ip)
async def search_documents(
    request: Request,
    response: Response,
    search_request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Search indexed documents using Hybrid Search (FAISS + BM25)."""
    import uuid
    user_uuid = uuid.UUID(current_user.id) if isinstance(current_user.id, str) else current_user.id

    # 1. Fetch valid document IDs for the user (to filter the FAISS index)
    stmt = select(Document).join(Course, Document.course_id == Course.id).where(
        Course.owner_id == user_uuid,
        Document.index_status == "ready"
    )

    if search_request.course_id:
        import uuid
        clean_cid = search_request.course_id.strip().replace(" ", "-")
        try:
            course_uuid = uuid.UUID(clean_cid) if isinstance(clean_cid, str) else clean_cid
            stmt = stmt.where(Course.id == course_uuid)
        except ValueError:
            return {"results": []}

    result = await db.execute(stmt)
    docs = result.scalars().all()

    valid_doc_ids = [doc.insightforge_doc_id for doc in docs if doc.insightforge_doc_id]

    if not valid_doc_ids:
        return {"results": []}

    try:
        import asyncio
        engine = InsightForgeEngine()
        # Retrieve chunks using the public engine API in a separate thread
        chunks = await asyncio.to_thread(
            engine.retrieve_chunks,
            search_request.query,
            valid_doc_ids,
            search_request.top_k
        )

        return {
            "results": [
                {
                    "content": c.content,
                    "score": c.score,
                    "page": c.page,
                    "document_id": c.document_id,
                }
                for c in chunks
            ]
        }
    except Exception as e:
        logger.exception(
            "Search engine error for user %s: %s",
            current_user.id,
            type(e).__name__,
        )
        raise HTTPException(
            status_code=500,
            detail="Search is temporarily unavailable. Please try again later.",
        )


class AISearchRequest(BaseModel):
    query: str
    course_id: str | None = None
    persona: str = "intermediate" # beginner, intermediate, expert, interview, exam
    style: str = "detailed" # shorter, deeper, examples, analogies
    top_k: int = 8

@router.post("/ai-query")
@limiter.limit("30/hour", key_func=_get_user_or_ip)
async def ai_synthesized_search(
    request: Request,
    response: Response,
    req: AISearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """AI Synthesized Search with multi-step reasoning, citations, and collapsible raw sources."""
    from services.search_service import SearchService
    service = SearchService(db)
    result = await service.ai_search(
        query=req.query,
        user_id=str(current_user.id),
        course_id=req.course_id,
        persona=req.persona,
        style=req.style,
        top_k=req.top_k,
    )
    return result

