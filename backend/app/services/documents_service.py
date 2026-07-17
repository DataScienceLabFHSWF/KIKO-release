import os, logging, time, asyncpg, re, json, yaml
from sqlalchemy import select, and_, delete, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException, status
from app.core import DocumentProcessor
from app.models import DocumentModel, EmbeddingModel
from .configuration_service import get_app_config_and_libary_available
from app.utils import is_probably_hashed_filename, compute_sha256, canonical_storage_path
from .embedding_service import generate_document_embeddings, store_embeddings_to_db, get_embeddings_from_db
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Tuple, Any, Optional
from datetime import date, datetime
from .course_markdown_parser_service import parse_course_markdown, CourseMarkdownStructureError
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()
BACKEND_API_URL = os.getenv("BACKEND_API_URL")

class MarkdownStructureError(Exception):
    """Raised when an uploaded markdown file does not match the required structure."""

def serialize_metadata(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, list):
        return [serialize_metadata(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serialize_metadata(item) for key, item in value.items()}
    return value

def split_markdown_sections(body: str) -> tuple[dict[str, str], list[str]]:
    sections: dict[str, str] = {}
    order: List[str] = []
    current_title: Optional[str] = None
    buffer: list[str] = []

    for line in body.splitlines():
        if line.startswith("## "):
            if current_title is not None:
                sections[current_title] = "\n".join(buffer).strip()
                buffer = []
            current_title = line[3:].strip()
            order.append(current_title)
        else:
            buffer.append(line)

    if current_title is not None:
        sections[current_title] = "\n".join(buffer).strip()

    normalized = {title.lower(): content for title, content in sections.items()}
    return normalized, order

def parse_structured_markdown(text: str) -> dict[str, Any]:
    front_matter_pattern = re.compile(r"^\ufeff?---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    front_match = front_matter_pattern.match(text)
    if not front_match:
        raise MarkdownStructureError("Markdown file must start with a YAML front matter block delimited by ---")

    front_content = front_match.group(1)
    body = text[front_match.end():]

    metadata_raw = yaml.safe_load(front_content) or {}
    if not isinstance(metadata_raw, dict):
        raise MarkdownStructureError("Front matter must be a YAML mapping of key/value pairs")
    metadata = serialize_metadata(metadata_raw)
    if not isinstance(metadata, dict):
        raise MarkdownStructureError("Front matter must resolve to a mapping after serialization")

    source_id = metadata.get("id")
    if not isinstance(source_id, str) or not source_id.strip():
        raise MarkdownStructureError("Front matter must include a non-empty 'id' field")

    sections_map, section_order = split_markdown_sections(body)

    required_sections = {
        "content": "Content",
        "quiz": "Quiz",
        "comprehension questions": "Comprehension Questions",
        "further reading": "Further reading",
    }

    missing = [display for key, display in required_sections.items() if not sections_map.get(key)]
    if missing:
        raise MarkdownStructureError(f"Markdown document missing required sections: {', '.join(missing)}")

    content_section = sections_map["content"].strip()
    quiz_section = sections_map["quiz"]
    comprehension_section = sections_map["comprehension questions"]
    further_section = sections_map["further reading"].strip()

    quiz_match = re.search(r"```quiz\s*(.*?)```", quiz_section, re.DOTALL | re.IGNORECASE)
    if not quiz_match:
        raise MarkdownStructureError("Quiz section must contain a ```quiz ...``` fenced block")
    quiz_yaml = yaml.safe_load(quiz_match.group(1)) or {}
    if not isinstance(quiz_yaml, dict):
        raise MarkdownStructureError("Quiz block must be a YAML mapping")

    questions_match = re.search(r"```questions\s*(.*?)```", comprehension_section, re.DOTALL | re.IGNORECASE)
    if not questions_match:
        raise MarkdownStructureError("Comprehension Questions section must contain a ```questions ...``` fenced block")
    questions_yaml = yaml.safe_load(questions_match.group(1)) or {}
    if not isinstance(questions_yaml, dict):
        raise MarkdownStructureError("Questions block must be a YAML mapping")

    questions_list = questions_yaml.get("questions")
    if not isinstance(questions_list, list) or not questions_list:
        raise MarkdownStructureError("Questions block must define a non-empty 'questions' list")

    qa_entries: list[dict[str, str]] = []
    for idx, item in enumerate(questions_list, start=1):
        if not isinstance(item, dict):
            raise MarkdownStructureError(f"Question entry #{idx} must be a mapping with 'question' and 'answer'")
        question_text = (item.get("question") or "").strip()
        answer_text = (item.get("answer") or "").strip()
        if not question_text or not answer_text:
            raise MarkdownStructureError(f"Question entry #{idx} must include both question and answer text")
        qa_entries.append({"question": question_text, "answer": answer_text})

    questions_dict = {"qa_list": qa_entries}

    quiz_yaml_str = yaml.safe_dump(quiz_yaml, sort_keys=False, allow_unicode=True).strip()

    learning_objectives = metadata.get("learning_objectives")
    summary_parts: list[str] = []
    title = metadata.get("title")
    if isinstance(title, str) and title.strip():
        summary_parts.append(title.strip())
    if isinstance(learning_objectives, list) and learning_objectives:
        objectives_lines = [f"- {str(obj)}" for obj in learning_objectives]
        summary_parts.append("Learning objectives:\n" + "\n".join(objectives_lines))

    content_block = content_section.strip()
    if content_block:
        summary_parts.append(content_block)

    combined_content = content_section
    if further_section:
        further_block = further_section.strip()
        if further_block:
            combined_content = f"{combined_content}\n\n## Further reading\n{further_block}"
            summary_parts.append(f"## Further reading\n{further_block}")

    summary_text = "\n\n".join(part for part in summary_parts if part).strip()
    if not summary_text:
        summary_text = combined_content.strip()

    language_hint = metadata.get("lang") or metadata.get("language") or "auto"

    return {
        "metadata": metadata,
        "content": combined_content.strip(),
        "summary": summary_text,
        "quiz_yaml_str": quiz_yaml_str,
        "quiz_dict": quiz_yaml,
        "questions_dict": questions_dict,
        "section_order": section_order,
        "language": language_hint,
    }

async def get_existing_doc_by_source_id(source_id: str, user_id: int, db: AsyncSession) -> Optional[DocumentModel]:
    if not source_id:
        return None
    
    try:
        json_id = json.dumps(source_id)

        stmt = (
            select(DocumentModel)
            .where(
                and_(
                    DocumentModel.uploaded_by == user_id,
                    cast(DocumentModel.doc_metadata["id"], String) == json_id,
                )
            )
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error while fetching document by source_id for user {user_id}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error while fetching document by source_id for user {user_id}: {str(e)}"
        )

async def prepare_document_replacement(doc: DocumentModel, db: AsyncSession) -> Optional[str]:
    """Remove embeddings and mark the document for deletion. Returns old storage path."""
    if not doc:
        return None

    try:
        old_path = doc.storage_path

        await db.execute(delete(EmbeddingModel).where(EmbeddingModel.document_id == doc.document_id))
        await db.delete(doc)
        await db.flush()

        return old_path
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error while preparing document replacement: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error while preparing document replacement: {str(e)}"
        )

def remove_file_safely(path: Optional[str]) -> None:
    if not path:
        return
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError as exc:
        logger.warning("Failed to remove replaced markdown file %s: %s", path, exc)

async def save_doc_to_db(
    file_name: str,
    content_hash: str,
    storage_path: str,
    uploader_id: int,
    doc_status: str,
    source_document_id: Optional[int],
    derivation_type: Optional[str],
    generation_config_hash: Optional[str],
    db: AsyncSession,
):
    """Save document metadata to the database."""
    
    try:
        print(f"ℹ️ Saving the {file_name} to Database.")
        doc = DocumentModel(
            file_name=file_name,
            content_hash= content_hash,
            storage_path= storage_path,
            uploaded_by= uploader_id,
            status=doc_status,
            source_document_id=source_document_id,
            derivation_type=derivation_type,
            generation_config_hash=generation_config_hash,
        )
        db.add(doc)
        await db.commit()
        print(f"✅ Successfully Saved the {file_name} to Database.")
        return doc
    except IntegrityError as e:
        await db.rollback()
        if isinstance(e.orig, asyncpg.exceptions.UniqueViolationError):
            # Custom handling for duplicate hash_file_name
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"❌ Document already exists with this hash (duplicate file): {str(e.orig)}"
            )
        else:
            # General DB error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"❌ Database error while saving document: {str(e)}"
            )

async def get_doc_by_hash_name(
    content_hash: str,
    user_id: int,
    db: AsyncSession,
    doc_status: str = "processed",
):
    """Retrieve a document by its hash file name and user ID.
    This function fetches a document from the database based on its hash file name, user ID, and status.
    It returns the document if found, or None if not found."""

    try:
        print(f"ℹ️ Getting the doc {content_hash} from database.")
        
        result = await db.execute(
            select(DocumentModel).where(
                and_(
                    DocumentModel.content_hash == content_hash,
                    DocumentModel.uploaded_by == user_id,
                    DocumentModel.status == doc_status
                )
            )
        )

        doc = result.scalar_one_or_none()
        
        if not doc:
            return None          
        
        print(f"✅ Successfully got the {content_hash} from database.")        
        return doc 
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error during getting doc {content_hash} from DB: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during getting doc {content_hash} from DB: {str(e)}"
        )

async def get_doc_by_derivation(
    source_document_id: int,
    derivation_type: str,
    generation_config_hash: str,
    user_id: int,
    db: AsyncSession,
    doc_status: str = "processed",
):
    try:
        result = await db.execute(
            select(DocumentModel).where(
                and_(
                    DocumentModel.uploaded_by == user_id,
                    DocumentModel.source_document_id == source_document_id,
                    DocumentModel.derivation_type == derivation_type,
                    DocumentModel.generation_config_hash == generation_config_hash,
                    DocumentModel.status == doc_status,
                )
            )
        )
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error during derivation doc lookup: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during derivation doc lookup: {str(e)}"
        )

async def update_doc_in_db(
    content_hash: str,
    processed_data: dict,
    doc_status: str,
    user_id: int,
    db: AsyncSession,
):
    """Update the document in the database with processed data.
    This function updates the document's content, metadata, and status in the database.
    It retrieves the document by its hash file name and user ID, then updates its fields with the provided processed data.
    If the document is not found, it raises an HTTPException."""

    try:
        print(f"ℹ️ Updating the docs {content_hash} from database.")
        doc_data = await get_doc_by_hash_name(content_hash, user_id, db, "uploaded")

        if not doc_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"❌ Document with hash {content_hash} not found for update."
            )

        chunks = processed_data.get("chunks", []) or []
        str_chunks = "\n".join(chunks)

        doc_data.doc_metadata = processed_data.get("doc_metadata", {})
        doc_data.doc_content = processed_data.get("doc_content") or str_chunks
        doc_data.content_metadatas = processed_data.get("metadatas", {})
        doc_data.tables = processed_data.get("tables", [])
        doc_data.vlm_texts = processed_data.get("vlm_texts", [])
        doc_data.processing_stats = processed_data.get("processing_stats", {})
        doc_data.status = doc_status

        await db.commit()
        print(f"✅ Successfully updated the {content_hash} in database.")
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error during Updating the doc {content_hash} in DB: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during updating the doc {content_hash} in DB: {str(e)}"
        )

async def process_pdf(
    file_name: str, 
    content_hash:str, 
    storage_path: str, 
    user_id:int, 
    db: AsyncSession,
    response_language: str
) -> dict:
    """
    Process the uploaded PDF file.
    This function reads the PDF file stream, processes it, and returns the extracted data.
    """

    try:
        print(f"ℹ️ process_pdf Service: Process PDF service.")

        print(f"ℹ️ process_pdf Service: getting application configuration and library availability.")
        config = await get_app_config_and_libary_available()
        print(f"ℹ️ process_pdf Service: Configuration loaded:")        

        # 🗃️ Store in DB
        doc = await save_doc_to_db(
            file_name,
            content_hash,
            storage_path,
            user_id,
            "uploaded",
            None,
            None,
            None,
            db,
        )

        print(f" ℹ️ Doc saved in DB: {doc.doc_content}")
        
        print("ℹ️ process_pdf Service: Initializing DocumentProcessor with config")
        document_processor = DocumentProcessor(config, response_language)
        
        print(f"ℹ️ process_pdf Service: Processing PDF file: {file_name} or {storage_path} with DocumentProcessor.")

        data = await document_processor.process_document(file_name, content_hash, storage_path)

        if data and "chunks" in data and len(data["chunks"]) > 0:
            # Update the DB
            await update_doc_in_db(content_hash, data, "processed", user_id, db)
            
            return data
        else:
            print("❌ No data extracted from the file.")
            return None
    except Exception as e:
        print(f"❌ process_pdf Service: Error processing PDF file {file_name}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"❌ process_pdf Service: Error processing PDF file {file_name}: {str(e)}")

async def process_markdown(
    file_name: str, 
    content_hash: str, 
    storage_path: str, 
    user_id: int, 
    db: AsyncSession,
    source_document_id: Optional[int] = None,
    derivation_type: Optional[str] = None,
    generation_config_hash: Optional[str] = None,
    skip_persistence: bool = False,
    existing_doc_id: Optional[int] = None,
) -> dict:
    """
    Process the uploaded Markdown file similarly to PDFs, but without OCR/VLM specifics.
    - Save Document row (status=uploaded)
    - Read markdown text, split to chunks, build minimal metadata
    - Update Document row (status=processed)
    Returns dict with keys: chunks, metadatas, doc_metadata, tables, processing_stats
    """

    try:
        print("ℹ️ process_markdown Service: Processing Markdown file.")
        config = await get_app_config_and_libary_available()

        with open(storage_path, "r", encoding="utf-8", errors="ignore") as fh:
            text = fh.read()
        
        if not text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="❌ Uploaded markdown file is empty.",
            )

        try:
            parsed = parse_course_markdown(text)
        except CourseMarkdownStructureError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc
        except yaml.YAMLError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"❌ Invalid YAML content in markdown: {exc}",
            ) from exc
        
        metadata = dict(parsed["metadata"])
        metadata.setdefault("source_type", "markdown")
        metadata.setdefault("file_name", file_name)
        metadata["content_hash"] = content_hash

        source_id = parsed.get("source_id")
        old_storage_path: Optional[str] = None

        if not skip_persistence and isinstance(source_id, str) and source_id:
            existing_doc = await get_existing_doc_by_source_id(source_id, user_id, db)
            if existing_doc:
                old_storage_path = await prepare_document_replacement(existing_doc, db)

        app_config = config.get("app_config") if isinstance(config, dict) else None
        chunk_size = getattr(app_config, "chunk_size", 1000) if app_config else 1000
        chunk_overlap = getattr(app_config, "chunk_overlap", 200) if app_config else 200

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

        doc_id: Optional[int] = existing_doc_id
        if not skip_persistence:
            doc = await save_doc_to_db(
                file_name,
                content_hash,
                storage_path,
                user_id,
                "uploaded",
                source_document_id,
                derivation_type,
                generation_config_hash,
                db,
            )
            doc_id = doc.document_id

        if doc_id is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="❌ Missing document id for markdown processing.",
            )

        metadata["document_id"] = doc_id

        chunks: list[str] = []
        metadatas: list[dict] = []

        for unit in parsed["embedding_units"]:
            unit_chunks = splitter.split_text(unit["text"] or "")
            if not unit_chunks:
                continue

            total_chunks_for_module = len(unit_chunks)
            for idx, chunk in enumerate(unit_chunks):
                chunks.append(chunk)
                metadatas.append(
                    {
                        "source": file_name,
                        "content_hash": content_hash,
                        "file_path": storage_path,
                        "document_type": "markdown",
                        "processing_method": "markdown_course_v1",
                        "document_id": doc_id,
                        "module_id": unit["module_id"],
                        "module_title": unit["module_title"],
                        "chunk_index_within_module": idx,
                        "total_chunks_within_module": total_chunks_for_module,
                        "title": (metadata.get("course") or {}).get("title"),
                    }
                )

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="❌ Markdown content is empty after preprocessing.",
            )

        result = {
            "doc_metadata": metadata,
            "doc_content": text,
            "chunks": chunks,
            "metadatas": metadatas,
            "tables": [],
            "processing_stats": {
                "total_chunks": len(chunks),
                "modules_count": len(parsed["course_json"].get("modules", [])),
                "questions_count": len(parsed["questions_dict"].get("qa_list", [])),
                "final_quiz_present": bool(parsed.get("quiz_dict")),
                "structure_version": "markdown_course_v1",
            },
            "summary": parsed["summary"],
            "questions_dict": parsed["questions_dict"],
            "quiz": parsed["quiz_yaml_str"],      # backward-compatible final quiz string
            "quiz_dict": parsed["quiz_dict"],
            "template_markdown": parsed["template_markdown"],
            "course_json": parsed["course_json"],
        }

        if not skip_persistence:
            await update_doc_in_db(content_hash, result, "processed", user_id, db)

            if old_storage_path and os.path.abspath(old_storage_path) != os.path.abspath(storage_path):
                remove_file_safely(old_storage_path)

        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ process_markdown Service: Error processing Markdown file {file_name}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ process_markdown Service: Error processing Markdown file {file_name}: {str(e)}",
        ) from e

async def process_folder_with_embeddings(
    absolute_folder_path: str,
    embedding_model_name: str,
    user_id: int,
    db: AsyncSession,
    response_language: str
) -> dict:
    """
    Process all PDFs in a folder for a given user:
    - Persist file by SHA256 content hash only once (content-addressed store)
    - Create Document row if not exists
    - Extract chunks + metadata
    - Generate embeddings and upsert (document_id, embedding_model, chunk_id) uniques
    Returns a summary + per-file status list.
    """

    if not os.path.isdir(absolute_folder_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"❌ Folder not found: {absolute_folder_path}")

    pdf_files = [f for f in os.listdir(absolute_folder_path) if f.lower().endswith(".pdf")]
    if not pdf_files:
        return {
            "message": "No_PDF",
            "summary": {"processed": 0, "skipped_existing": 0, "failed": 0, "elapsed_sec": 0.0},
            "files": []
        }

    processed, skipped, failed = 0, 0, 0
    results = []
    t0 = time.time()

    for filename in pdf_files:
        if is_probably_hashed_filename(filename):
            # Skip already materialized hash-named file in source folder
            results.append({"file_name": filename, "status": "skipped_source_hash"})
            skipped += 1
            continue

        src_path = os.path.join(absolute_folder_path, filename)
        try:
            with open(src_path, "rb") as fh:
                content = fh.read()
            if not content:
                results.append({"file_name": filename, "status": "error", "message": "empty file"})
                failed += 1
                continue

            content_hash = compute_sha256(content)
            storage_path = canonical_storage_path(content_hash)

            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            if not os.path.exists(storage_path):
                with open(storage_path, "wb") as out:
                    out.write(content)

            # check if already processed for this user
            doc = await get_doc_by_hash_name(content_hash, user_id, db)
            if doc:
                # Also check if embeddings already exist for this model
                embeddings_data = await get_embeddings_from_db(
                        content_hash= content_hash,
                        embedding_model= embedding_model_name,
                        user_id= user_id,
                        db = db
                )
                if embeddings_data:
                    results.append({"file_name": filename, "status": "exists"})
                    skipped += 1
                    continue
            
            # Not processed: run pipeline
            processed_data = await process_pdf(filename, content_hash, storage_path, user_id, db, response_language)
            
            if not processed_data or not processed_data.get("chunks"):
                results.append({"file_name": filename, "status": "error", "message": "no chunks"})
                failed += 1
                continue

            # create embeddings
            emb = await generate_document_embeddings(
                processed_data["chunks"], 
                model_name=embedding_model_name
            )

            # reload the doc row
            doc = await get_doc_by_hash_name(content_hash, user_id, db)
            
            if not doc:
                results.append({"file_name": filename, "status": "error", "message": "doc not saved"})
                failed += 1
                continue

            await store_embeddings_to_db(
                chunks=processed_data["chunks"],
                metadatas=processed_data["metadatas"],
                embeddings=emb,
                embedding_model_name=embedding_model_name,
                doc_id=doc.document_id,
                user_id=user_id,
                db=db
            )

            results.append({
                "file_name": filename,
                "status": "processed",
                "embeddings_created": len(processed_data["chunks"])
            })
            processed += 1

        except Exception as e:
            results.append({"file_name": filename, "status": "error", "message": str(e)})
            failed += 1

    elapsed = time.time() - t0
    return {
        "message": "success",
        "summary": {
            "processed": processed,
            "skipped_existing": skipped,
            "failed": failed,
            "elapsed_sec": round(elapsed, 2),
        },
        "files": results,
    }

async def list_user_documents(
    user_id: int, 
    db: AsyncSession
) -> List[DocumentModel]:
    """
    Return all documents that belong to a user, newest first.
    """

    try:
        print(f"ℹ️ Getting the all doc from database for user {user_id}.")
        
        result = await db.execute(
            select(DocumentModel)
            .where(DocumentModel.uploaded_by == user_id)
            .order_by(DocumentModel.uploaded_at.desc())
        )

        doc_list = result.scalars().all()

        print(f"✅ Successfully got the {len(doc_list)} docs from database.")
        return doc_list
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error during getting all docs from DB: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during getting all docs from DB: {str(e)}"
        )

async def delete_user_document(
    document_id: int, 
    user_id: int, 
    db: AsyncSession
) -> bool:
    """
    Delete a single document and its embeddings if the user owns it.
    Returns True if a document was deleted, False otherwise.
    """

    try:
        print(f"ℹ️ Deleting the document {document_id} from database for user {user_id}.")
        
        # Delete embeddings associated with this doc & user (safety guard)
        await db.execute(
            delete(EmbeddingModel)
            .where(
                EmbeddingModel.document_id == document_id,
                EmbeddingModel.doc_uploaded_by == user_id,
            )
        )
        
        # Delete the document itself        
        await db.execute(
            delete(DocumentModel)
            .where(
                DocumentModel.document_id == document_id,
                DocumentModel.uploaded_by == user_id,
            )
        )
        
        await db.commit()
        return True
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error during deleting document {document_id} from DB for the user {user_id}: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during deleting document {document_id} from DB for the user {user_id}: {str(e)}"
        )

async def delete_all_user_documents(
    user_id: int, 
    db: AsyncSession
) -> Tuple[int, int]:
    """
    Delete ALL documents for a user, along with their embeddings.
    Returns (num_docs_deleted, num_embeddings_deleted).
    """
    
    try:
        # First, get all doc ids for this user
        doc_ids_stmt = select(DocumentModel.document_id).where(DocumentModel.uploaded_by == user_id)
        res = await db.execute(doc_ids_stmt)
        doc_ids = [row[0] for row in res.all()]
        
        if not doc_ids:
            return (0, 0)
        
        # Delete embeddings
        emb_result = await db.execute(
            delete(EmbeddingModel)
            .where(
                EmbeddingModel.document_id.in_(doc_ids),
                EmbeddingModel.doc_uploaded_by == user_id,
            )
        )
        
        # Delete documents
        doc_result = await db.execute(
            delete(DocumentModel)
            .where(
                DocumentModel.document_id.in_(doc_ids),
                DocumentModel.uploaded_by == user_id,
            )
        )
        
        await db.commit()
        
        # rowcount can be None on some backends; guard with fallback to 0
        emb_deleted = emb_result.rowcount or 0
        docs_deleted = doc_result.rowcount or 0
        return (docs_deleted, emb_deleted)
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error during deleting all documents from DB for the user {user_id}: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during deleting all documents from DB for the user {user_id}: {str(e)}"
        )
