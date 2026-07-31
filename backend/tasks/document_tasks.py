"""Document indexing background task."""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone

from core.exceptions import InsightForgeError
from insightforge.engine import InsightForgeEngine

logger = logging.getLogger(__name__)


async def process_document(document_id: str | uuid.UUID) -> dict:
    """Async service function to handle DB operations and document indexing synchronously."""
    from db.session import get_db_session
    from db.models.document import Document
    from sqlalchemy import select, func
    import uuid
    import traceback

    try:
        doc_uuid = uuid.UUID(document_id) if isinstance(document_id, str) else document_id
    except ValueError:
        doc_uuid = document_id
    logger.info("Entering process_document(%s)", doc_uuid)

    async with get_db_session() as session:
        # Fetch document
        stmt = select(Document).where(Document.id == doc_uuid)
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
            logger.info("Loading InsightForgeEngine for document_id=%s", document_id)
            engine = InsightForgeEngine()
            
            ProgressTracker.set_stage(document_id, "generating_embeddings", 60, "Generating SentenceTransformer embeddings")
            
            # Run indexing in a thread pool with a hard timeout.
            # The first-ever call may take 60-120s on Render free tier because
            # SentenceTransformer (all-MiniLM-L6-v2, ~80 MB) must be downloaded
            # from HuggingFace Hub. Subsequent calls are fast (model is cached).
            # Without a timeout, a hung thread leaves status=processing forever.
            INDEXING_TIMEOUT_SECONDS = 300  # 5 minutes: generous for first cold download
            logger.info(
                "Calling engine.index_document(%s) via thread pool (timeout=%ds)...",
                doc.stored_path,
                INDEXING_TIMEOUT_SECONDS,
            )
            try:
                index_result = await asyncio.wait_for(
                    asyncio.to_thread(engine.index_document, doc.stored_path),
                    timeout=INDEXING_TIMEOUT_SECONDS,
                )
            except asyncio.TimeoutError:
                elapsed = round(time.perf_counter() - t_start, 1)
                msg = (
                    f"Document indexing timed out after {elapsed}s "
                    f"(limit={INDEXING_TIMEOUT_SECONDS}s). "
                    "This usually means the SentenceTransformer model is still downloading "
                    "on a cold Render instance. Re-upload after 2-3 minutes to retry "
                    "once the model is cached."
                )
                logger.error("Indexing timeout for document_id=%s: %s", document_id, msg)
                doc.index_status = "error"
                session.add(doc)
                await session.commit()
                ProgressTracker.set_stage(document_id, "failed", 0, msg)
                return {"status": "error", "message": msg}

            logger.info("Finished indexing for document_id=%s, chunk_count=%d", document_id, index_result.chunk_count)

            t_index = round((time.perf_counter() - t_start) * 1000, 2)
            ProgressTracker.record_timing(document_id, "index_creation_ms", t_index)
            ProgressTracker.set_stage(document_id, "building_search_index", 85, "Building FAISS and BM25 search index")

            # Update DB with success
            t_db_start = time.perf_counter()
            doc.insightforge_doc_id = index_result.doc_id
            doc.chunk_count = index_result.chunk_count
            doc.index_status = "ready"
            doc.indexed_at = func.now()
            
            session.add(doc)
            await session.commit()

            t_db = round((time.perf_counter() - t_db_start) * 1000, 2)
            ProgressTracker.record_timing(document_id, "db_write_ms", t_db)
            ProgressTracker.set_stage(document_id, "completed", 100, "Document indexed successfully")
            
            logger.info(
                "Successfully indexed document %s in %.0fms (chunks=%d)",
                document_id,
                t_index,
                index_result.chunk_count,
            )
            return {"status": "success", "doc_id": document_id}
            
        except InsightForgeError as e:
            logger.exception(
                "InsightForge error indexing document %s",
                document_id,
            )
            doc.index_status = "error"
            session.add(doc)
            await session.commit()
            from core.progress import ProgressTracker
            ProgressTracker.set_stage(document_id, "failed", 0, f"Document indexing failed: {type(e).__name__}: {str(e)}")
            raise
        except Exception as e:
            logger.exception(
                "Unexpected error indexing document %s",
                document_id,
            )
            doc.index_status = "error"
            session.add(doc)
            await session.commit()
            from core.progress import ProgressTracker
            ProgressTracker.set_stage(document_id, "failed", 0, f"Unexpected error: {type(e).__name__}: {str(e)}")
            raise



# Alias for backward compatibility with existing tests
_process_document_async = process_document


