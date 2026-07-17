from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, UniqueConstraint
from pgvector.sqlalchemy import Vector
from datetime import datetime, timezone
from app.database import Base
from sqlalchemy.orm import relationship

class EmbeddingModel(Base):
    """Model for storing document embeddings in the database.
    This model includes fields for embedding ID, chunks, metadata, embedding vector,
    embedding model, creation time, and the associated document ID.
    It is used to manage embeddings related to documents within the application."""
    
    __tablename__ = "docs_embeddings"

    embedding_id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(Integer, nullable=False)
    chunks = Column(String, nullable=False)
    metadatas = Column(JSON, nullable=False)
    embedding = Column(Vector(768), nullable=False)
    embedding_model = Column(String, nullable=False)    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.document_id"), nullable=False)
    doc_uploaded_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("document_id", "embedding_model", "chunk_id", name="uq_doc_model_chunk"),
    )
    
    document = relationship("DocumentModel", back_populates="embeddings")
