"""Document indexing background task."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from tasks.celery_app import celery_app
from core.exceptions import InsightForgeError
from insightforge.engine import InsightForgeEngine

logger = logging.getLogger(__name__)


async def _process_document_async(document_id: str) -> dict:
    """Async wrapper to handle DB operations for document processing."""
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
            # Init InsightForge Engine
            engine = InsightForgeEngine()
            
            # Call adapter to index the document via the public engine API
            logger.info(f"Indexing document {document_id} via InsightForge...")
            index_result = engine.index_document(doc.stored_path)

            # Update DB with success
            doc.insightforge_doc_id = index_result.doc_id
            doc.chunk_count = index_result.chunk_count
            doc.index_status = "ready"
            doc.indexed_at = datetime.now(timezone.utc)
            
            session.add(doc)
            await session.commit()
            
            logger.info(f"Successfully indexed document {document_id}")
            return {"status": "success", "doc_id": document_id}
            
        except InsightForgeError as e:
            logger.error(f"InsightForge error indexing document {document_id}: {e}")
            doc.index_status = "error"
            session.add(doc)
            await session.commit()
            raise  # Reraise for Celery retry mechanism
        except Exception as e:
            logger.error(f"Unexpected error indexing document {document_id}: {e}")
            doc.index_status = "error"
            session.add(doc)
            await session.commit()
            raise


@celery_app.task(
    name="tasks.process_document",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def process_document_task(self, document_id: str) -> dict:  # type: ignore[override]
    """
    Background task: index a document using InsightForge-AI adapter.
    """
    try:
        return asyncio.run(_process_document_async(document_id))
    except Exception as exc:
        logger.error(f"Task failed, retrying... {exc}")
        raise self.retry(exc=exc)
