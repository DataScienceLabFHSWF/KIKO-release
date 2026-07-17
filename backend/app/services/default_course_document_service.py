# backend/app/services/default_course_document_service.py
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from .documents_service import get_doc_by_hash_name, process_markdown
from app.utils import compute_sha256, canonical_storage_path_for_ext
from .embedding_service import (
    store_embeddings_to_db, generate_document_embeddings, get_embeddings_from_db
)

DEFAULT_TEMPLATE_EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "nomic-embed-text:v1.5",
)

async def provision_markdown_document_for_course(
    user_id: int,
    course_id: int,
    file_name: str,
    markdown_text: str,
    db: AsyncSession,
    embedding_model_name: str | None = None,
) -> dict:
    """
    Creates a DocumentModel + chunks + embeddings for an already-created course.

    This makes default template courses visible in:
    - My Documents
    - Chat assistant / RAG retrieval
    """

    embedding_model_name = embedding_model_name or DEFAULT_TEMPLATE_EMBEDDING_MODEL

    if not markdown_text or not markdown_text.strip():
        return {
            "ok": False,
            "reason": "empty_markdown",
            "file_name": file_name,
            "course_id": course_id,
        }

    markdown_bytes = markdown_text.encode("utf-8")
    content_hash = compute_sha256(markdown_bytes)
    storage_path = canonical_storage_path_for_ext(content_hash, "md")

    Path(storage_path).parent.mkdir(parents=True, exist_ok=True)

    if not os.path.exists(storage_path):
        with open(storage_path, "wb") as f:
            f.write(markdown_bytes)

    existing_doc = await get_doc_by_hash_name(
        content_hash=content_hash,
        user_id=user_id,
        db=db,
    )

    processed_data = await process_markdown(
        file_name=file_name,
        content_hash=content_hash,
        storage_path=storage_path,
        user_id=user_id,
        db=db,
        skip_persistence=existing_doc is not None,
        existing_doc_id=existing_doc.document_id if existing_doc else None,
    )

    if not processed_data or not processed_data.get("chunks"):
        return {
            "ok": False,
            "reason": "no_chunks",
            "file_name": file_name,
            "course_id": course_id,
        }

    doc = existing_doc or await get_doc_by_hash_name(
        content_hash=content_hash,
        user_id=user_id,
        db=db,
    )

    if not doc:
        return {
            "ok": False,
            "reason": "document_not_created",
            "file_name": file_name,
            "course_id": course_id,
        }

    existing_embeddings = await get_embeddings_from_db(
        content_hash=content_hash,
        embedding_model=embedding_model_name,
        user_id=user_id,
        db=db,
    )

    if existing_embeddings:
        return {
            "ok": True,
            "reason": "already_embedded",
            "document_id": doc.document_id,
            "file_name": file_name,
            "course_id": course_id,
        }

    embeddings = await generate_document_embeddings(
        processed_data["chunks"],
        model_name=embedding_model_name,
    )

    if not embeddings:
        return {
            "ok": False,
            "reason": "embedding_failed",
            "document_id": doc.document_id,
            "file_name": file_name,
            "course_id": course_id,
        }

    await store_embeddings_to_db(
        chunks=processed_data["chunks"],
        metadatas=processed_data["metadatas"],
        embeddings=embeddings,
        embedding_model_name=embedding_model_name,
        doc_id=doc.document_id,
        user_id=user_id,
        db=db,
    )

    return {
        "ok": True,
        "reason": "created",
        "document_id": doc.document_id,
        "file_name": file_name,
        "course_id": course_id,
        "chunks": len(processed_data["chunks"]),
    }
