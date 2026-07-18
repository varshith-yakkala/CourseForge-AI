"""Document upload and management routes."""
import os
import uuid
import shutil
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.deps import get_current_active_user, get_db
from api.documents.schemas import DocumentResponse
from db.models.document import Document
from db.models.course import Course
from db.models.user import User
from datetime import datetime, timezone

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    course_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Upload a PDF document and link it to a course."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    # Verify course exists and belongs to user
    stmt = select(Course).where(
        Course.id == course_id, 
        Course.owner_id == current_user.id,
        Course.deleted_at.is_(None)
    )
    result = await db.execute(stmt)
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Check if course already has a document
    stmt_doc = select(Document).where(Document.course_id == course_id)
    result_doc = await db.execute(stmt_doc)
    if result_doc.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Course already has an uploaded document")

    # Mock storage
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_id = uuid.uuid4()
    stored_path = os.path.join(UPLOAD_DIR, f"{file_id}.pdf")
    
    file_size_bytes = 0
    with open(stored_path, "wb") as buffer:
        while True:
            chunk = await file.read(1024 * 1024)  # 1MB chunks
            if not chunk:
                break
            buffer.write(chunk)
            file_size_bytes += len(chunk)
            
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
    
    # Trigger background indexing
    from tasks.document_tasks import process_document_task
    process_document_task.delay(str(doc.id))
    
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
    
    from tasks.document_tasks import process_document_task
    process_document_task.delay(str(doc.id))
    
    return doc
