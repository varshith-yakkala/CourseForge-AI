"""Document indexing background task."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from core.exceptions import InsightForgeError
from insightforge.engine import InsightForgeEngine

logger = logging.getLogger(__name__)


async def process_document(document_id: str) -> dict:
    """Async service function to handle DB operations and document indexing synchronously."""
    from db.session import get_db_session
    from db.models.document import Document
    from sqlalchemy import select

    async with get_db_session() as session:
        # Fetch document
        stmt = select(Document).where(Document.id == document_id)
        result = await session.execute(stmt)
        doc = result.scalar_one_or_none()

        if not doc:
            logger.error(f"Document {document_id} not found.")
            return {"status": "error", "message": "Document not found"}

        # Update status to processing
        doc.index_status = "processing"
        session.add(doc)
        await session.commit()

        try:
            from core.progress import ProgressTracker
            import time

            t_start = time.perf_counter()
            ProgressTracker.set_stage(document_id, "extracting_text", 30, "Extracting text from PDF pages")
            
            # Init InsightForge Engine
            engine = InsightForgeEngine()
            
            ProgressTracker.set_stage(document_id, "generating_embeddings", 60, "Generating SentenceTransformer embeddings")
            
            # Call adapter to index the document via thread pool to keep event loop responsive
            logger.info(f"Indexing document {document_id} via InsightForge...")
            index_result = await asyncio.to_thread(engine.index_document, doc.stored_path)

            t_index = round((time.perf_counter() - t_start) * 1000, 2)
            ProgressTracker.record_timing(document_id, "index_creation_ms", t_index)
            ProgressTracker.set_stage(document_id, "building_search_index", 85, "Building FAISS and BM25 search index")

            # Update DB with success
            t_db_start = time.perf_counter()
            doc.insightforge_doc_id = index_result.doc_id
            doc.chunk_count = index_result.chunk_count
            doc.index_status = "ready"
            doc.indexed_at = datetime.now(timezone.utc)
            
            session.add(doc)
            await session.commit()

            t_db = round((time.perf_counter() - t_db_start) * 1000, 2)
            ProgressTracker.record_timing(document_id, "db_write_ms", t_db)
            ProgressTracker.set_stage(document_id, "completed", 100, "Document indexed successfully")
            
            logger.info(
                f"Successfully indexed document {document_id}",
                extra={
                    "document_id": document_id,
                    "chunk_count": index_result.chunk_count,
                    "index_creation_ms": t_index,
                    "db_write_ms": t_db,
                    "status": "ready"
                }
            )
            return {"status": "success", "doc_id": document_id}
            
        except InsightForgeError as e:
            logger.error(f"InsightForge error indexing document {document_id}: {e}", extra={"document_id": document_id, "error": str(e)})
            doc.index_status = "error"
            session.add(doc)
            await session.commit()
            from core.progress import ProgressTracker
            ProgressTracker.set_stage(document_id, "failed", 0, "Document indexing failed")
            raise
        except Exception as e:
            logger.error(f"Unexpected error indexing document {document_id}: {e}", extra={"document_id": document_id, "error": str(e)})
            doc.index_status = "error"
            session.add(doc)
            await session.commit()
            from core.progress import ProgressTracker
            ProgressTracker.set_stage(document_id, "failed", 0, "An unexpected error occurred during indexing")
            raise



# Alias for backward compatibility with existing tests
_process_document_async = process_document


