import asyncio
import json
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import PromptManager
from app.database import AsyncSessionLocal
from app.models import DocumentModel, EmbeddingModel
from app.services.configuration_service import get_app_config_and_libary_available
from app.services.course_creator_manager import AsyncBatchProcessor
from app.services.documents_service import (
    get_doc_by_derivation,
    get_doc_by_hash_name,
    process_markdown,
    remove_file_safely,
    save_doc_to_db,
)
from app.services.embedding_service import (
    generate_document_embeddings,
    get_embeddings_from_db,
    store_embeddings_to_db,
)
from app.utils import (
    canonical_storage_path,
    canonical_storage_path_for_ext,
    compute_sha256,
)

FINAL_JOB_STATUSES = {"completed", "cancelled", "failed"}
MAX_RETAINED_FINAL_JOBS = 100
FINAL_JOB_RETENTION = timedelta(minutes=30)


@dataclass
class CourseUploadJob:
    job_id: str
    user_id: int
    file_name: str
    status: str = "queued"
    progress: float = 0.0
    message: str = "Queued"
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    cancel_requested: bool = False
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    task: Optional[asyncio.Task] = None
    created_document_ids: set[int] = field(default_factory=set)
    stage_key: str = "queued"

    def snapshot(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "progress": round(min(max(self.progress, 0.0), 1.0), 4),
            "message": self.message,
            "cancel_requested": self.cancel_requested,
            "stage_key": self.stage_key,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "result": self.result,
            "error": self.error,
        }


class CourseUploadJobManager:
    def __init__(
        self,
        *,
        max_retained_final_jobs: int = MAX_RETAINED_FINAL_JOBS,
        final_job_retention: timedelta = FINAL_JOB_RETENTION,
    ) -> None:
        if max_retained_final_jobs < 1:
            raise ValueError("max_retained_final_jobs must be at least 1")
        if final_job_retention <= timedelta(0):
            raise ValueError("final_job_retention must be positive")

        self._jobs: dict[str, CourseUploadJob] = {}
        self._lock = asyncio.Lock()
        self._max_retained_final_jobs = max_retained_final_jobs
        self._final_job_retention = final_job_retention

    def _prune_final_jobs_locked(
        self,
        *,
        now: Optional[datetime] = None,
        protected_job_id: Optional[str] = None,
    ) -> None:
        """Prune expired and excess final jobs while preserving active work."""
        current_time = now or datetime.now(timezone.utc)
        expiration_cutoff = current_time - self._final_job_retention
        final_jobs = sorted(
            (
                candidate
                for candidate in self._jobs.values()
                if candidate.status in FINAL_JOB_STATUSES
            ),
            key=lambda candidate: (
                candidate.updated_at,
                candidate.created_at,
                candidate.job_id,
            ),
        )

        for candidate in final_jobs:
            if (
                candidate.job_id != protected_job_id
                and candidate.updated_at <= expiration_cutoff
            ):
                self._jobs.pop(candidate.job_id, None)

        retained_final_jobs = [
            candidate
            for candidate in final_jobs
            if candidate.job_id in self._jobs
        ]
        excess_count = max(
            0,
            len(retained_final_jobs) - self._max_retained_final_jobs,
        )
        for candidate in retained_final_jobs:
            if excess_count == 0:
                break
            if candidate.job_id == protected_job_id:
                continue
            self._jobs.pop(candidate.job_id, None)
            excess_count -= 1

    async def _prune_final_jobs(
        self,
        *,
        now: Optional[datetime] = None,
        protected_job_id: Optional[str] = None,
    ) -> None:
        async with self._lock:
            self._prune_final_jobs_locked(
                now=now,
                protected_job_id=protected_job_id,
            )

    async def start_pdf_job(
        self,
        *,
        user_id: int,
        file_name: str,
        file_bytes: bytes,
        embedding_model_name: str,
        llm_model_name: str,
        response_language: str,
        qa_count: int,
        quiz_question_count: int,
        quiz_option_count: int,
        misconception_count: int,
    ) -> CourseUploadJob:
        job = CourseUploadJob(
            job_id=str(uuid.uuid4()),
            user_id=user_id,
            file_name=file_name,
            status="queued",
            progress=0.01,
            message="Queued PDF processing job.",
            stage_key="queued",
        )
        async with self._lock:
            self._jobs[job.job_id] = job
            self._prune_final_jobs_locked()

        job.task = asyncio.create_task(
            self._run_pdf_job(
                job=job,
                file_bytes=file_bytes,
                embedding_model_name=embedding_model_name,
                llm_model_name=llm_model_name,
                response_language=response_language,
                qa_count=qa_count,
                quiz_question_count=quiz_question_count,
                quiz_option_count=quiz_option_count,
                misconception_count=misconception_count,
            )
        )
        return job

    async def get_job(self, job_id: str, user_id: int) -> CourseUploadJob:
        async with self._lock:
            self._prune_final_jobs_locked()
            job = self._jobs.get(job_id)

        if not job or job.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="❌ Upload job not found.",
            )

        return job

    async def cancel_job(self, job_id: str, user_id: int) -> CourseUploadJob:
        job = await self.get_job(job_id, user_id)

        if job.status in FINAL_JOB_STATUSES:
            return job

        job.cancel_requested = True
        job.status = "cancelling"
        job.message = "Cancellation requested. Stopping the PDF job..."
        job.stage_key = "cancelling"
        job.updated_at = datetime.now(timezone.utc)

        if job.task and not job.task.done():
            job.task.cancel()

        return job

    async def _set_progress(
        self,
        job: CourseUploadJob,
        progress: float,
        message: str,
        stage_key: str,
    ) -> None:
        if job.status in FINAL_JOB_STATUSES:
            return

        if job.cancel_requested:
            job.status = "cancelling"
        else:
            job.status = "processing"

        job.progress = max(job.progress, min(max(progress, 0.0), 0.99))
        job.message = message
        job.stage_key = stage_key
        job.updated_at = datetime.now(timezone.utc)

    async def _ensure_not_cancelled(self, job: CourseUploadJob) -> None:
        if job.cancel_requested:
            raise asyncio.CancelledError
        if asyncio.current_task() and asyncio.current_task().cancelled():
            raise asyncio.CancelledError

    async def _run_pdf_job(
        self,
        *,
        job: CourseUploadJob,
        file_bytes: bytes,
        embedding_model_name: str,
        llm_model_name: str,
        response_language: str,
        qa_count: int,
        quiz_question_count: int,
        quiz_option_count: int,
        misconception_count: int,
    ) -> None:
        async with AsyncSessionLocal() as db:
            try:
                await self._set_progress(
                    job,
                    0.05,
                    "Preparing PDF upload...",
                    "prepare_upload",
                )
                await self._ensure_not_cancelled(job)

                content_hash = compute_sha256(file_bytes)
                storage_path = canonical_storage_path(content_hash)

                if not os.path.exists(storage_path):
                    os.makedirs(os.path.dirname(storage_path), exist_ok=True)
                    with open(storage_path, "wb") as storage_file:
                        storage_file.write(file_bytes)

                existing_pdf_doc = await get_doc_by_hash_name(
                    content_hash,
                    job.user_id,
                    db,
                )
                if existing_pdf_doc:
                    job.result = {
                        "message": "file_exists",
                        "detail": f"File '{job.file_name}' is already processed.",
                    }
                    job.status = "completed"
                    job.progress = 1.0
                    job.message = "This PDF was already processed earlier."
                    job.stage_key = "completed"
                    job.updated_at = datetime.now(timezone.utc)
                    return

                await self._set_progress(
                    job,
                    0.1,
                    "Saving uploaded PDF...",
                    "save_pdf",
                )
                pdf_doc = await save_doc_to_db(
                    job.file_name,
                    content_hash,
                    storage_path,
                    job.user_id,
                    "processed",
                    None,
                    None,
                    None,
                    db,
                )
                job.created_document_ids.add(pdf_doc.document_id)
                await self._ensure_not_cancelled(job)

                generation_config_hash = compute_sha256(
                    json.dumps(
                        {
                            "pipeline": "course_markdown_v1",
                            "llm_model": llm_model_name,
                            "response_language": response_language,
                            "qa_count": qa_count,
                            "quiz_question_count": quiz_question_count,
                            "quiz_option_count": quiz_option_count,
                            "misconception_count": misconception_count,
                        },
                        sort_keys=True,
                    ).encode("utf-8")
                )

                linked_markdown_doc = await get_doc_by_derivation(
                    source_document_id=pdf_doc.document_id,
                    derivation_type="course_markdown",
                    generation_config_hash=generation_config_hash,
                    user_id=job.user_id,
                    db=db,
                )

                if linked_markdown_doc:
                    await self._set_progress(
                        job,
                        0.82,
                        "Reusing previously generated markdown...",
                        "reuse_cached_markdown",
                    )
                    await self._ensure_not_cancelled(job)

                    existing_embeddings = await get_embeddings_from_db(
                        content_hash=linked_markdown_doc.content_hash,
                        embedding_model=embedding_model_name,
                        user_id=job.user_id,
                        db=db,
                    )

                    processed_markdown_data = await process_markdown(
                        linked_markdown_doc.file_name,
                        linked_markdown_doc.content_hash,
                        linked_markdown_doc.storage_path,
                        job.user_id,
                        db,
                        skip_persistence=True,
                        existing_doc_id=linked_markdown_doc.document_id,
                    )

                    if not existing_embeddings:
                        await self._set_progress(
                            job,
                            0.9,
                            "Generating embeddings for cached markdown...",
                            "generate_embeddings",
                        )
                        await self._ensure_not_cancelled(job)

                        markdown_embeddings = await generate_document_embeddings(
                            processed_markdown_data["chunks"],
                            model_name=embedding_model_name,
                        )
                        if not markdown_embeddings:
                            raise HTTPException(
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=(
                                    "❌ Failed to generate embeddings for existing "
                                    "generated markdown."
                                ),
                            )

                        await self._set_progress(
                            job,
                            0.96,
                            "Storing embeddings for cached markdown...",
                            "store_embeddings",
                        )
                        await self._ensure_not_cancelled(job)

                        await store_embeddings_to_db(
                            processed_markdown_data["chunks"],
                            processed_markdown_data["metadatas"],
                            markdown_embeddings,
                            embedding_model_name=embedding_model_name,
                            doc_id=linked_markdown_doc.document_id,
                            user_id=job.user_id,
                            db=db,
                        )

                    job.result = {
                        "message": "success",
                        "final_summary": processed_markdown_data.get("summary"),
                        "questions": processed_markdown_data.get("questions_dict"),
                        "quiz": processed_markdown_data.get("quiz"),
                        "generated_markdown": linked_markdown_doc.doc_content,
                        "generated_markdown_file_name": linked_markdown_doc.file_name,
                        "metadata": processed_markdown_data.get("doc_metadata"),
                        "template_markdown": processed_markdown_data.get(
                            "template_markdown"
                        ),
                        "course_json": processed_markdown_data.get("course_json"),
                    }
                    job.status = "completed"
                    job.progress = 1.0
                    job.message = "PDF processing finished."
                    job.stage_key = "completed"
                    job.updated_at = datetime.now(timezone.utc)
                    return

                configs = await get_app_config_and_libary_available()
                if not configs:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="❌ Application configuration not available.",
                    )

                prompt_mgr = PromptManager(configs)
                processor = AsyncBatchProcessor(
                    prompt_mgr,
                    llm_model_name=llm_model_name,
                    response_language=response_language,
                )

                course_data = await processor.summarize_document(
                    storage_path,
                    qa_count=qa_count,
                    quiz_question_count=quiz_question_count,
                    quiz_option_count=quiz_option_count,
                    misconception_count=misconception_count,
                    progress_callback=lambda progress, message: self._set_progress(
                        job,
                        progress,
                        message,
                        self._stage_key_for_progress(progress),
                    ),
                    cancellation_check=lambda: self._ensure_not_cancelled(job),
                )
                await self._ensure_not_cancelled(job)

                generated_markdown = course_data.get("generated_markdown")
                if not isinstance(generated_markdown, str) or not generated_markdown.strip():
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="❌ Generated markdown is empty.",
                    )

                await self._set_progress(
                    job,
                    0.94,
                    "Saving generated markdown...",
                    "save_generated_markdown",
                )
                await self._ensure_not_cancelled(job)

                generated_markdown_bytes = generated_markdown.encode("utf-8")
                generated_markdown_hash = compute_sha256(generated_markdown_bytes)
                generated_markdown_path = canonical_storage_path_for_ext(
                    generated_markdown_hash,
                    "md",
                )
                generated_markdown_file_name = (
                    course_data.get("generated_markdown_file_name")
                    or "generated-course.md"
                )

                if not os.path.exists(generated_markdown_path):
                    os.makedirs(os.path.dirname(generated_markdown_path), exist_ok=True)
                    with open(generated_markdown_path, "wb") as generated_file:
                        generated_file.write(generated_markdown_bytes)

                await self._set_progress(
                    job,
                    0.96,
                    "Parsing generated markdown...",
                    "parse_generated_markdown",
                )
                await self._ensure_not_cancelled(job)

                processed_markdown_data = await process_markdown(
                    generated_markdown_file_name,
                    generated_markdown_hash,
                    generated_markdown_path,
                    job.user_id,
                    db,
                    source_document_id=pdf_doc.document_id,
                    derivation_type="course_markdown",
                    generation_config_hash=generation_config_hash,
                )

                markdown_doc = await get_doc_by_hash_name(
                    generated_markdown_hash,
                    job.user_id,
                    db,
                )
                if not markdown_doc:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=(
                            "❌ Generated markdown document not stored correctly in DB."
                        ),
                    )
                job.created_document_ids.add(markdown_doc.document_id)

                await self._set_progress(
                    job,
                    0.98,
                    "Generating embeddings...",
                    "generate_embeddings",
                )
                await self._ensure_not_cancelled(job)

                markdown_embeddings = await generate_document_embeddings(
                    processed_markdown_data["chunks"],
                    model_name=embedding_model_name,
                )
                if not markdown_embeddings:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=(
                            "❌ Failed to generate embeddings for generated markdown. "
                            "Please check embedding model configuration."
                        ),
                    )

                await self._set_progress(
                    job,
                    0.99,
                    "Storing embeddings...",
                    "store_embeddings",
                )
                await self._ensure_not_cancelled(job)

                await store_embeddings_to_db(
                    processed_markdown_data["chunks"],
                    processed_markdown_data["metadatas"],
                    markdown_embeddings,
                    embedding_model_name=embedding_model_name,
                    doc_id=markdown_doc.document_id,
                    user_id=job.user_id,
                    db=db,
                )

                job.result = {
                    "message": "success",
                    "final_summary": processed_markdown_data.get("summary"),
                    "questions": processed_markdown_data.get("questions_dict"),
                    "quiz": processed_markdown_data.get("quiz"),
                    "generated_markdown": generated_markdown,
                    "generated_markdown_file_name": generated_markdown_file_name,
                    "metadata": processed_markdown_data.get("doc_metadata"),
                    "template_markdown": processed_markdown_data.get(
                        "template_markdown"
                    ),
                    "course_json": processed_markdown_data.get("course_json"),
                }
                job.status = "completed"
                job.progress = 1.0
                job.message = "PDF processing finished."
                job.stage_key = "completed"
                job.updated_at = datetime.now(timezone.utc)
            except asyncio.CancelledError:
                await self._cleanup_job_artifacts(job, db)
                job.status = "cancelled"
                job.message = "PDF processing was cancelled."
                job.error = None
                job.stage_key = "cancelled"
                job.updated_at = datetime.now(timezone.utc)
            except HTTPException as exc:
                await self._cleanup_job_artifacts(job, db)
                job.status = "failed"
                job.error = exc.detail
                job.message = "PDF processing failed."
                job.stage_key = "failed"
                job.updated_at = datetime.now(timezone.utc)
            except Exception as exc:
                await self._cleanup_job_artifacts(job, db)
                job.status = "failed"
                job.error = str(exc)
                job.message = "PDF processing failed."
                job.stage_key = "failed"
                job.updated_at = datetime.now(timezone.utc)
            finally:
                async with self._lock:
                    job.task = None
                    if job.status in FINAL_JOB_STATUSES:
                        self._prune_final_jobs_locked(
                            protected_job_id=job.job_id,
                        )

    def _stage_key_for_progress(self, progress: float) -> str:
        if progress < 0.16:
            return "read_pdf"
        if progress < 0.64:
            return "summarize_chunks"
        if progress < 0.76:
            return "combine_summary"
        if progress < 0.82:
            return "generate_quiz"
        if progress < 0.88:
            return "generate_misconceptions"
        if progress < 0.94:
            return "generate_questions"
        return "finalize_markdown"

    async def _cleanup_job_artifacts(
        self,
        job: CourseUploadJob,
        db: AsyncSession,
    ) -> None:
        document_ids = sorted(job.created_document_ids, reverse=True)
        if not document_ids:
            return

        for document_id in document_ids:
            try:
                result = await db.execute(
                    select(DocumentModel).where(
                        DocumentModel.document_id == document_id,
                        DocumentModel.uploaded_by == job.user_id,
                    )
                )
                document = result.scalar_one_or_none()
                if not document:
                    continue

                storage_path = document.storage_path

                await db.execute(
                    delete(EmbeddingModel).where(
                        EmbeddingModel.document_id == document_id,
                        EmbeddingModel.doc_uploaded_by == job.user_id,
                    )
                )
                await db.execute(
                    delete(DocumentModel).where(
                        DocumentModel.document_id == document_id,
                        DocumentModel.uploaded_by == job.user_id,
                    )
                )
                await db.commit()

                remaining_refs_result = await db.execute(
                    select(func.count(DocumentModel.document_id)).where(
                        DocumentModel.storage_path == storage_path
                    )
                )
                remaining_refs = remaining_refs_result.scalar_one() or 0
                if remaining_refs == 0:
                    remove_file_safely(storage_path)
            except Exception:
                await db.rollback()


course_upload_job_manager = CourseUploadJobManager()
