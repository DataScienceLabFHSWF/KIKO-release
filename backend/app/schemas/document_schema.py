# Schema for document
from pydantic import BaseModel
from datetime import datetime

# This is a Pydantic model for document data
class Document(BaseModel):
    """Document Schema for representing a document in the system.
    This Schema includes fields for document ID, name, upload time, and the user who uploaded it."""
    
    id: int
    name: str
    upload_time: datetime
    uploaded_by: int

class DocumentResponse(BaseModel):
    """Response Schema for document details.
    This Schema represents the detailed information of a document including its ID, file name,
    content hash, storage path, status, upload time, and processing statistics."""
    
    document_id: int
    file_name: str
    content_hash: str
    storage_path: str | None = None
    status: str | None = None
    uploaded_at: datetime
    processing_stats: dict | None = None
