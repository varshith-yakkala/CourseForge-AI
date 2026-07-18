"""Document schemas."""
from datetime import datetime
import uuid
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    owner_id: uuid.UUID
    original_filename: str
    file_size_bytes: int
    mime_type: str
    page_count: int | None = None
    index_status: str
    created_at: datetime
    
    model_config = {"from_attributes": True}
