# backend/app/schemas/document_schema.py
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Any, Literal

class DocumentResponse(BaseModel):
    """Response Schema for document details.
    This Schema represents the detailed information of a document including its ID, file name,
    content hash, storage path, status, upload time, and processing statistics."""
    
    model_config = ConfigDict(from_attributes=True)
    document_id: int
    file_name: str
    content_hash: str
    storage_path: str | None = None
    status: str | None = None
    uploaded_at: datetime
    processing_stats: dict | None = None

class DocumentProcessingFileResponse(BaseModel):
    """Schema for individual file processing response.
    This Schema represents the response for each file processed during document upload, including the file name,
    processing status, content hash, and any relevant messages or statistics."""

    file_name: str | None = None
    status: Literal["processed", "exists", "error"]
    content_hash: str | None = None
    message: str | None = None
    embeddings_count: int | None = None
    processing_stats: dict[str, Any] | None = None
    generated_markdown_hash: str | None = None
    generated_markdown_file_name: str | None = None

class DocumentProcessingSummaryResponse(BaseModel):
    """Schema for document processing summary response.
    This Schema represents the summary of the document processing results, including the total number of files found,
    the number of files processed, skipped due to existing content, failed during processing, and the elapsed time for processing."""
    
    processed: int
    skipped_existing: int
    failed: int
    elapsed_sec: float

class ProcessUploadedDocsResponse(BaseModel):
    """Schema for the response after processing uploaded documents.
    This Schema represents the overall response after processing uploaded documents, including a success message,
    a summary of the processing results, and a list of individual file processing responses."""
    
    message: Literal["success"]
    summary: DocumentProcessingSummaryResponse
    files: list[DocumentProcessingFileResponse] = Field(default_factory=list)

class BatchProcessingDataResponse(BaseModel):
    """Schema for batch processing data response.
    This Schema represents the data returned after batch processing of documents, including the generated chunks,
    associated metadata, processing time, and counts of files found, processed, and skipped."""
    
    chunks: list[str] = Field(default_factory=list)
    metadatas: list[dict[str, Any]] = Field(default_factory=list)
    processing_time: float
    files_found: int
    files_processed: int
    files_skipped: int

class BatchProcessingResponse(BaseModel):
    """Schema for batch processing response.
    This Schema represents the response after batch processing of documents, including a success message and the data returned from the processing, 
    which may include generated chunks, metadata, and processing statistics. If no PDF files were found during processing, 
    the message will indicate "No_PDF" and the data may be empty or contain relevant information about the processing attempt.
    """
    
    message: Literal["success", "No_PDF"]
    data: BatchProcessingDataResponse | dict[str, Any] | None = None

class DeleteDocumentsResponse(BaseModel):
    """Schema for delete documents response.
    This Schema represents the response after attempting to delete documents, including a message indicating the result of 
    the deletion attempt and the count of documents that were deleted."""
    deleted_count: int
