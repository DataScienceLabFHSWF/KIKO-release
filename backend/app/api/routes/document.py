# backend/app/api/routes/document.py

import os, logging, time, json
from fastapi import (APIRouter, UploadFile, File, HTTPException, Depends, Form, status)
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import (
    require_role, process_pdf, get_doc_by_hash_name,
    process_markdown, generate_document_embeddings, store_embeddings_to_db,
    get_embeddings_from_db, get_app_config_and_libary_available, AsyncBatchProcessor,
    get_doc_by_derivation, get_user_profile_by_email, list_user_documents, 
    delete_user_document, delete_all_user_documents, get_request_lang,
)
from app.database import get_db
from app.utils import (
    compute_sha256, canonical_storage_path, canonical_storage_path_for_ext, 
    is_probably_hashed_filename
)
from typing import Any
from app.schemas import (
    DocumentResponse, COMMON_ERROR_RESPONSES, ProcessUploadedDocsResponse,
    DocumentProcessingFileResponse, BatchProcessingResponse
)
from app.core import PromptManager
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(responses=COMMON_ERROR_RESPONSES)

BASE_DATA_DIR = Path("/backend/data").resolve()

async def _get_current_user_profile(user: dict, db: AsyncSession):
    """
    Helper function to get the current user's profile from the database. Raises HTTPException if the user is not found.
    This function abstracts the logic of retrieving the user's profile based on their email, which is expected to be present in the 'user' dictionary provided by the authentication dependency. 
    It ensures that if the user profile cannot be found in the database, an appropriate HTTPException is raised with a 404 status code.
    """
    user_profile = await get_user_profile_by_email(user["email"], db)

    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user_profile

def _resolve_batch_folder(folder_path: str) -> Path:
    """
    Resolve user-provided folder_path safely under /backend/data.
    Prevents accidental path traversal.
    """

    raw = folder_path.strip()

    if not raw:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="folder_path is required.",
        )

    relative = raw.lstrip("/")

    if relative.startswith("backend/data/"):
        relative = relative.removeprefix("backend/data/")
    elif relative.startswith("data/"):
        relative = relative.removeprefix("data/")

    resolved = (BASE_DATA_DIR / relative).resolve()

    if BASE_DATA_DIR not in resolved.parents and resolved != BASE_DATA_DIR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Folder path is outside the allowed data directory.",
        )

    return resolved

async def _process_pdf_through_markdown_pipeline(
    file_name: str,
    file_content: bytes,
    embedding_model_name: str,
    user_id: int,
    response_language: str,
    db: AsyncSession,
) -> dict[str, Any]:
    """Process PDF, generate course markdown, then process markdown and embed markdown chunks only."""

    content_hash = compute_sha256(file_content)
    storage_path = canonical_storage_path(content_hash)

    os.makedirs(os.path.dirname(storage_path), exist_ok=True)
    if not os.path.exists(storage_path):
        with open(storage_path, "wb") as f:
            f.write(file_content)

    existing_pdf_doc = await get_doc_by_hash_name(content_hash, user_id, db)
    if not existing_pdf_doc:
        processed_pdf_data = await process_pdf(
            file_name,
            content_hash,
            storage_path,
            user_id,
            db,
            response_language,
        )

        if (
            not processed_pdf_data
            or "chunks" not in processed_pdf_data
            or len(processed_pdf_data["chunks"]) == 0
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="❌ No data extracted from the file.",
            )

        existing_pdf_doc = await get_doc_by_hash_name(content_hash, user_id, db)
        if not existing_pdf_doc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="❌ PDF document not stored correctly in DB.",
            )

    configs = await get_app_config_and_libary_available(db=db)
    if not configs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="❌ App configuration not found",
        )

    app_config = configs.get("app_config") if isinstance(configs, dict) else None
    if isinstance(app_config, dict):
        default_llm_model = app_config.get("default_llm_model")
    else:
        default_llm_model = getattr(app_config, "default_llm_model", None)

    if not default_llm_model:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Missing default_llm_model in app configuration.",
        )

    generation_config_hash = compute_sha256(
        json.dumps(
            {
                "pipeline": "chat_markdown_v1",
                "llm_model": default_llm_model,
                "response_language": response_language,
            },
            sort_keys=True,
        ).encode("utf-8")
    )

    linked_markdown_doc = await get_doc_by_derivation(
        source_document_id=existing_pdf_doc.document_id,
        derivation_type="chat_markdown",
        generation_config_hash=generation_config_hash,
        user_id=user_id,
        db=db,
    )

    if linked_markdown_doc:
        existing_embeddings = await get_embeddings_from_db(
            content_hash=linked_markdown_doc.content_hash,
            embedding_model=embedding_model_name,
            user_id=user_id,
            db=db,
        )

        if existing_embeddings and len(existing_embeddings) > 0:
            return {
                "status": "exists",
                "content_hash": content_hash,
                "generated_markdown_hash": linked_markdown_doc.content_hash,
                "generated_markdown_file_name": linked_markdown_doc.file_name,
                "message": "ℹ️ PDF markdown and embeddings already processed for this model.",
            }

        processed_markdown_data = await process_markdown(
            linked_markdown_doc.file_name,
            linked_markdown_doc.content_hash,
            linked_markdown_doc.storage_path,
            user_id,
            db,
            skip_persistence=True,
            existing_doc_id=linked_markdown_doc.document_id,
        )

        markdown_embeddings = await generate_document_embeddings(
            processed_markdown_data["chunks"],
            model_name=embedding_model_name,
        )
        if (
            markdown_embeddings is None
            or not isinstance(markdown_embeddings, list)
            or len(markdown_embeddings) == 0
        ):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="❌ Failed to generate embeddings for existing generated markdown.",
            )

        await store_embeddings_to_db(
            processed_markdown_data["chunks"],
            processed_markdown_data["metadatas"],
            markdown_embeddings,
            embedding_model_name=embedding_model_name,
            doc_id=linked_markdown_doc.document_id,
            user_id=user_id,
            db=db,
        )

        return {
            "status": "processed",
            "content_hash": content_hash,
            "generated_markdown_hash": linked_markdown_doc.content_hash,
            "generated_markdown_file_name": linked_markdown_doc.file_name,
            "processed_markdown_data": processed_markdown_data,
            "embeddings_count": len(markdown_embeddings),
        }

    prompt_mgr = PromptManager(configs)
    processor = AsyncBatchProcessor(
        prompt_mgr,
        llm_model_name=default_llm_model,
        response_language=response_language,
    )

    course_data = await processor.summarize_document(storage_path)
    generated_markdown = course_data.get("generated_markdown")
    generated_markdown_file_name = course_data.get("generated_markdown_file_name") or "generated-course.md"

    if not isinstance(generated_markdown, str) or not generated_markdown.strip():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Generated markdown is empty.",
        )

    generated_markdown_bytes = generated_markdown.encode("utf-8")
    generated_markdown_hash = compute_sha256(generated_markdown_bytes)
    generated_markdown_path = canonical_storage_path_for_ext(generated_markdown_hash, "md")

    if not os.path.exists(generated_markdown_path):
        os.makedirs(os.path.dirname(generated_markdown_path), exist_ok=True)
        with open(generated_markdown_path, "wb") as generated_file:
            generated_file.write(generated_markdown_bytes)

    processed_markdown_data = await process_markdown(
        generated_markdown_file_name,
        generated_markdown_hash,
        generated_markdown_path,
        user_id,
        db,
        source_document_id=existing_pdf_doc.document_id,
        derivation_type="chat_markdown",
        generation_config_hash=generation_config_hash,
    )

    if (
        not processed_markdown_data
        or "chunks" not in processed_markdown_data
        or len(processed_markdown_data["chunks"]) == 0
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="❌ No data extracted from generated markdown.",
        )

    markdown_embeddings = await generate_document_embeddings(
        processed_markdown_data["chunks"],
        model_name=embedding_model_name,
    )

    if (
        markdown_embeddings is None
        or not isinstance(markdown_embeddings, list)
        or len(markdown_embeddings) == 0
    ):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Failed to generate embeddings for generated markdown.",
        )

    markdown_doc = await get_doc_by_hash_name(generated_markdown_hash, user_id, db)
    if not markdown_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="❌ Generated markdown document not stored correctly in DB.",
        )

    await store_embeddings_to_db(
        processed_markdown_data["chunks"],
        processed_markdown_data["metadatas"],
        markdown_embeddings,
        embedding_model_name=embedding_model_name,
        doc_id=markdown_doc.document_id,
        user_id=user_id,
        db=db,
    )

    return {
        "status": "processed",
        "content_hash": content_hash,
        "generated_markdown_hash": generated_markdown_hash,
        "generated_markdown_file_name": generated_markdown_file_name,
        "processed_markdown_data": processed_markdown_data,
        "embeddings_count": len(markdown_embeddings),
    }

@router.post(
    "/process_uploaded_docs",
    response_model=ProcessUploadedDocsResponse,
    operation_id="process_uploaded_documents"
)
async def process_uploaded_docs(
    files: list[UploadFile] = File(...),
    embedding_model_name: str = Form(...),
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db)
) -> ProcessUploadedDocsResponse:
    """Process one or more PDF files:
    - Persist by SHA-256 hash (dedupe on content).
    - If doc already exists, return existing embeddings for the requested model.
    - If embeddings for this model are missing, generate & upsert.
    """   
    try:
        logger.info(f"ℹ️ process_uploaded_docs API: File {files} upload initiated by {user}.")

        if not files:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="❌ No Files uploaded.")
        
        user_profile = await _get_current_user_profile(user, db)
        
        user_id = user_profile.user_id
        
        logger.info(f"ℹ️ process_uploaded_docs API : got user details {user_profile}")
        
        t0 = time.time()
        results: list[DocumentProcessingFileResponse] = []
        processed_count = 0
        skipped_existing = 0
        failed = 0
        
        for upload in files:
            file_result = {
                "file_name": upload.filename,
                "status": None,
                "content_hash": None,
                "message": None,
                "embeddings": None,
            }

            logger.info(f"ℹ️ Processing before docs: {file_result}")

            try:
                content = await upload.read()

                if not content:
                    file_result.update(
                        status="error",
                        message="Empty file"
                    )

                    failed += 1
                    results.append(DocumentProcessingFileResponse.model_validate(file_result))
                    continue

                unified_result = await _process_pdf_through_markdown_pipeline(
                    file_name=upload.filename,
                    file_content=content,
                    embedding_model_name=embedding_model_name,
                    user_id=user_id,
                    response_language=response_language,
                    db=db,
                )

                file_result["content_hash"] = unified_result.get("content_hash")

                if unified_result.get("status") == "exists":
                    file_result.update(
                        status="exists",
                        message=unified_result.get(
                            "message", 
                            "ℹ️ Document already processed."
                        ),
                    )
                    skipped_existing += 1
                    results.append(DocumentProcessingFileResponse.model_validate(file_result))
                    continue

                processed_markdown_data = unified_result.get("processed_markdown_data") or {}
                
                file_result.update(
                    status="processed",
                    message="✅ Processed via markdown pipeline & embedded successfully.",
                    embeddings_count=unified_result.get("embeddings_count", 0),
                    processing_stats=processed_markdown_data.get("processing_stats"),
                    generated_markdown_hash=unified_result.get("generated_markdown_hash"),
                    generated_markdown_file_name=unified_result.get("generated_markdown_file_name"),
                )
                processed_count += 1
                results.append(DocumentProcessingFileResponse.model_validate(file_result))
            except Exception as e:
                logger.exception("❌ Error processing uploaded document")
                file_result.update(
                    status="error", 
                    message=str(e)
                )
                failed += 1
                results.append(DocumentProcessingFileResponse.model_validate(file_result))
        
        elapsed = time.time() - t0

        logger.info("✅ process_uploaded_docs API: Processing completed", extra={"elapsed_sec": round(elapsed, 2)})
        
        return ProcessUploadedDocsResponse(
            message="success",
            summary={
                "processed": processed_count,
                "skipped_existing": skipped_existing,
                "failed": failed,
                "elapsed_sec": round(elapsed, 2),
            },
            files=results,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ process_uploaded_docs failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        ) from e

@router.post(
    "/batch_processing",
    response_model=BatchProcessingResponse,
    operation_id="process_document_batch"
)
async def process_batch_docs(
    folder_path: str = Form(...),
    embedding_model_name: str = Form(...),
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db)
) -> BatchProcessingResponse:
    """Endpoint to process a batch of PDF files in a folder.
    This endpoint allows users with the roles 'Learner' or 'Instructor' to process all PDF files in a specified folder.
    The files are read and processed, and a response is returned indicating success or failure.
    """    
    try:
        logger.info(f"ℹ️ batch_processing API: {folder_path} AND {embedding_model_name} ")

        # /backend/data/EducTUM/ = /backend + /data/EducTUM/
        exact_folder_path = _resolve_batch_folder(folder_path)

        if not exact_folder_path.is_dir():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Folder not found: {folder_path}",
            )
        
        # Process PDFs with state-of-the-art models
        pdf_files = [
            file_path
            for file_path in exact_folder_path.iterdir()
            if file_path.is_file()
            and file_path.suffix.lower() == ".pdf"
            and not is_probably_hashed_filename(file_path.name)
        ]
        
        if not pdf_files:
            logger.error(f"❌ No PDF files found in the folder: {exact_folder_path}")
            return BatchProcessingResponse(
                message="No_PDF",
                data={
                    "folder_path": folder_path,
                    "files_found": 0,
                },
            )
        
        logger.info(f"ℹ️ Found {len(pdf_files)} PDF files in the folder: {exact_folder_path}")
        
        user_profile = await _get_current_user_profile(user, db)
        
        logger.info(f"ℹ️ batch_processing API : got user details {user_profile} and {user_profile.user_id}")
        
        all_chunks: list[str] = []
        all_metadatas: list[dict[str, Any]] = []
        processing_time_start = time.time()
        files_processed = 0
        files_skipped = 0

        for file_path in pdf_files:
            file_content = file_path.read_bytes()

            if not file_content:
                files_skipped += 1
                continue

            unified_result = await _process_pdf_through_markdown_pipeline(
                file_name=file_path.name,
                file_content=file_content,
                embedding_model_name=embedding_model_name,
                user_id=user_profile.user_id,
                response_language=response_language,
                db=db,
            )

            if unified_result.get("status") == "exists":
                files_skipped += 1
                continue

            processed_markdown_data = unified_result.get("processed_markdown_data") or {}

            all_chunks.extend(processed_markdown_data.get("chunks", []))
            all_metadatas.extend(processed_markdown_data.get("metadatas", []))
            files_processed += 1

        processing_time = time.time() - processing_time_start

        return BatchProcessingResponse(
            message="success",
            data={
                "chunks": all_chunks,
                "metadatas": all_metadatas,
                "processing_time": round(processing_time, 2),
                "files_found": len(pdf_files),
                "files_processed": files_processed,
                "files_skipped": files_skipped,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ batch_processing API: Error processing file path {folder_path}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get(
    "/my_docs", 
    response_model=list[DocumentResponse],
    operation_id="list_my_documents"
)
async def get_my_documents(
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    lang: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db)
) -> list[DocumentResponse]:
    """
    Return all documents uploaded by the authenticated user (newest first).
    """
    try:
        logger.info(f"ℹ️ my_docs API: Get all docs for user.")
        
        user_profile = await _get_current_user_profile(user, db)

        docs = await list_user_documents(user_profile.user_id, db)

        logger.info(f"✅ my_docs API: Retrieved {len(docs)} documents for user_id: {user_profile.user_id}")
        
        return [
            DocumentResponse.model_validate(doc)
            for doc in docs
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ my_docs API: Error processing get my docs: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete(
    "/delete_doc/{document_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_document"
)
async def delete_document(
    document_id: int,
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a single document (and its embeddings) if it belongs to the user.
    """
    try:
        logger.info(f"ℹ️ delete doc API: delete selected docs for user.")
        
        user_profile = await _get_current_user_profile(user, db)
        
        deleted = await delete_user_document(document_id, user_profile.user_id, db)
        
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ Document not found")
        
        logger.info(f"✅ delete doc API: Document {document_id} deleted for user_id: {user_profile.user_id}")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ delete_doc API: Error processing get my docs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        ) from e 

@router.delete(
    "/delete_all_doc", 
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_all_documents"
)
async def delete_all_documents(
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete ALL documents belonging to the authenticated user (and their embeddings).
    """
    try:
        logger.info(f"ℹ️ delete all doc API: delete ALL docs for user.")
        
        user_profile = await _get_current_user_profile(user, db)
        
        await delete_all_user_documents(user_profile.user_id, db)

        logger.info(f"✅ delete all doc API: All documents deleted for user_id: {user_profile.user_id}")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ delete_all_doc API: Error processing get my docs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        ) from e
