"""Document upload and management routes."""
import logging
import os
import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.deps import get_current_active_user, get_db
from api.documents.schemas import DocumentResponse
from core.config import settings
from core.rate_limit import limiter, _get_user_or_ip
from db.models.document import Document
from db.models.course import Course
from db.models.user import User
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents"])

# PDF magic bytes: all valid PDFs begin with %PDF-
_PDF_MAGIC = b"%PDF-"
# Chunk size for streaming upload (64 KB — small enough to keep memory low)
_CHUNK_SIZE = 64 * 1024


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour", key_func=_get_user_or_ip)
async def upload_document(
    request: Request,
    response: Response,
    course_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Upload a PDF document and link it to a course.

    Security hardening (Phase 1):
      - Rate limited: 10 uploads/hour per authenticated user
      - MIME type validated (Content-Type header)
      - File size limit enforced by streaming (MAX_UPLOAD_SIZE_MB config)
      - PDF magic bytes validated (%PDF-) after first chunk write
      - Partial files deleted on any validation failure
    """
    # ── MIME type check (client-provided, quick first gate) ──────────────────
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are supported. Please upload a .pdf file.",
        )

    # ── Verify course ownership ───────────────────────────────────────────────
    stmt = select(Course).where(
        Course.id == course_id,
        Course.owner_id == current_user.id,
        Course.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # ── Prevent duplicate uploads ─────────────────────────────────────────────
    stmt_doc = select(Document).where(Document.course_id == course_id)
    result_doc = await db.execute(stmt_doc)
    if result_doc.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Course already has an uploaded document")

    # ── Prepare storage ───────────────────────────────────────────────────────
    upload_dir = str(settings.upload_dir_path)
    os.makedirs(upload_dir, exist_ok=True)
    file_id = uuid.uuid4()
    stored_path = os.path.join(upload_dir, f"{file_id}.pdf")

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    file_size_bytes = 0
    magic_verified = False

    try:
        with open(stored_path, "wb") as buffer:
            while True:
                chunk = await file.read(_CHUNK_SIZE)
                if not chunk:
                    break

                # ── Size enforcement (streaming) ──────────────────────────────
                file_size_bytes += len(chunk)
                if file_size_bytes > max_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=(
                            f"File exceeds the maximum allowed size of "
                            f"{settings.MAX_UPLOAD_SIZE_MB} MB."
                        ),
                    )

                buffer.write(chunk)

                # ── Magic-byte validation (first chunk only) ──────────────────
                if not magic_verified:
                    if not chunk[:5] == _PDF_MAGIC:
                        raise HTTPException(
                            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            detail=(
                                "The uploaded file does not appear to be a valid PDF. "
                                "Please upload a genuine PDF document."
                            ),
                        )
                    magic_verified = True

    except HTTPException:
        # Clean up partial file on any validation failure
        if os.path.exists(stored_path):
            os.remove(stored_path)
            logger.info("Deleted partial upload after validation failure: %s", stored_path)
        raise

    # ── Persist document record ───────────────────────────────────────────────
    doc = Document(
        course_id=course_id,
        owner_id=current_user.id,
        original_filename=file.filename or "unknown.pdf",
        stored_path=stored_path,
        file_size_bytes=file_size_bytes,
        mime_type="application/pdf",
        index_status="pending",
        created_at=datetime.now(timezone.utc)
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # ── Execute document indexing synchronously ──────────────────────────────
    from core.progress import ProgressTracker
    import time
    t_start = time.perf_counter()
    ProgressTracker.set_stage(str(doc.id), "uploading_pdf", 15, "PDF file validated and stored")

    from tasks.document_tasks import process_document
    await process_document(str(doc.id))
    await db.refresh(doc)

    t_total = round((time.perf_counter() - t_start) * 1000, 2)
    ProgressTracker.record_timing(str(doc.id), "total_processing_ms", t_total)
    response.headers["X-Processing-Time-ms"] = str(t_total)

    return doc


@router.get("/course/{course_id}", response_model=DocumentResponse)
async def get_document_by_course(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get document details by course ID."""
    stmt = select(Document).where(
        Document.course_id == course_id,
        Document.owner_id == current_user.id
    )
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return doc


@router.get("/{document_id}/progress")
async def get_document_progress(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get real-time document indexing stage progress and execution metrics."""
    from core.progress import ProgressTracker
    stmt = select(Document).where(
        Document.id == document_id,
        Document.owner_id == current_user.id
    )
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    progress = ProgressTracker.get_progress(str(document_id))
    progress["index_status"] = doc.index_status
    return progress


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get document details."""
    stmt = select(Document).where(
        Document.id == document_id,
        Document.owner_id == current_user.id
    )
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return doc


@router.post("/{document_id}/retry", response_model=DocumentResponse)
async def retry_document_indexing(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Retry indexing a failed document."""
    stmt = select(Document).where(
        Document.id == document_id,
        Document.owner_id == current_user.id
    )
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.index_status == "ready":
        raise HTTPException(status_code=400, detail="Document is already indexed successfully")

    doc.index_status = "pending"
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    from tasks.document_tasks import process_document
    await process_document(str(doc.id))
    await db.refresh(doc)

    return doc




