# backend/app/schemas/chat_assistant_schema.py
from pydantic import BaseModel, Field
from typing import Any, Literal
from datetime import datetime

class ChatQueryRequest(BaseModel):
    """Request Schema for chatbot queries. This Schema represents the input for a chatbot query.
    It includes the query string, the embedding model to use, and the LLM model for generating responses."""
    
    query: str
    embedding_model: str
    llm_model: str

class ChatSourceDocumentResponse(BaseModel):
    """Response Schema for source documents retrieved during a chatbot query. 
    This Schema represents the information about a source document that was used to generate a response. 
    It includes details about the document, its location, and how it was processed."""
    
    source: str | None = None
    content_hash: str | None = None
    file_path: str | None = None
    document_type: str | None = None
    processing_method: str | None = None

    document_id: int | None = None
    module_id: str | None = None
    module_title: str | None = None
    chunk_index_within_module: int | None = None
    total_chunks_within_module: int | None = None

    title: str | None = None
    search_query: str | None = None
    retrieved_chunks: str | None = None
    search_timestamp: str | datetime | None = None

class ChatAnswerResponse(BaseModel):
    """Response Schema for chatbot answers. This Schema represents the output of a chatbot query, including the generated answer 
    and any source documents that were used to create the response.
    It includes the answer string and a list of source documents that provide context for the answer."""
    
    answer: str
    source_docs: list[ChatSourceDocumentResponse] = Field(default_factory=list)

class ChatQueryResponse(BaseModel):
    """Response Schema for chatbot query results. This Schema represents the complete response to a chatbot query, 
    including the generated answer and any relevant source documents. It includes a nested structure where the main response contains the 
    answer and a list of source documents that were used to generate the answer."""
    
    data: ChatAnswerResponse

class ChatMessageResponse(BaseModel):
    """Response Schema for individual chat messages. This Schema represents a single message in a chat conversation, 
    including the role of the sender (user, assistant, or system), the content of the message, 
    a timestamp, and any source documents associated with the message."""
    
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime | None = None
    sources: list[ChatSourceDocumentResponse] = Field(default_factory=list)

class ChatHistoryResponse(BaseModel):
    """Response Schema for chat history. This Schema represents the entire history of a chat conversation, 
    including all messages exchanged between the user and the assistant. It includes a list of individual chat messages, 
    each with its own role, content, timestamp, and associated source documents."""
    
    messages: list[ChatMessageResponse]
