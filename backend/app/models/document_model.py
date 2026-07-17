from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, UniqueConstraint
from datetime import datetime, timezone
from app.database import Base
from sqlalchemy.orm import relationship

class DocumentModel(Base):
    """Model for storing document information in the database.
    This model includes fields for document ID, file name, hash file name, file path,
    document metadata, content, content metadata, tables, VLM texts, processing statistics,
    status, upload time, and the user who uploaded the document.
    It is used to manage documents within the application."""
    
    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    storage_path = Column(String, nullable=False)      # /backend/data/uploaded_docs/<hash>.pdf
    doc_metadata = Column(JSON)
    doc_content = Column(String)
    content_metadatas = Column(JSON)
    tables = Column(JSON)
    vlm_texts = Column(JSON)
    processing_stats = Column(JSON)
    status = Column(String)
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    source_document_id = Column(Integer, ForeignKey("documents.document_id"), nullable=True, index=True)
    derivation_type = Column(String, nullable=True, index=True)
    generation_config_hash = Column(String(64), nullable=True, index=True)

    __table_args__ = (
        UniqueConstraint("content_hash", "uploaded_by", name="uq_doc_contenthash_user"),
        UniqueConstraint(
            "uploaded_by",
            "source_document_id",
            "derivation_type",
            "generation_config_hash",
            name="uq_doc_derivation_per_user",
        ),
    )    

    uploaded_by_user = relationship("UserModel", back_populates="documents")
    embeddings = relationship("EmbeddingModel", back_populates="document")
