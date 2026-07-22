"""Search routes."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.deps import get_current_active_user, get_db
from pydantic import BaseModel
from db.models.user import User
from db.models.course import Course
from db.models.document import Document
from insightforge.engine import InsightForgeEngine

router = APIRouter(prefix="/search", tags=["Search"])

class SearchRequest(BaseModel):
    query: str
    course_id: str | None = None
    top_k: int = 10

@router.post("")
async def search_documents(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Search indexed documents using Hybrid Search (FAISS + BM25)."""
    # 1. Fetch valid document IDs for the user (to filter the FAISS index)
    stmt = select(Document).join(Course).where(
        Course.owner_id == current_user.id,
        Document.index_status == "ready"
    )
    
    if request.course_id:
        stmt = stmt.where(Course.id == request.course_id)
        
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
            request.query,
            valid_doc_ids,
            request.top_k
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
        raise HTTPException(status_code=500, detail=str(e))
