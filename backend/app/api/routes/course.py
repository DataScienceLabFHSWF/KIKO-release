# backend/app/api/routes/course.py

import os, json, logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form, Body, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import FileResponse
from typing import Any
from app.services import (
    require_role, process_markdown, get_doc_by_hash_name,
    generate_document_embeddings, store_embeddings_to_db, 
    get_user_profile_by_email, AsyncBatchProcessor, grade_user_answer,
    create_course_with_summary_and_qas_for_instructor,
    list_courses_for_instructor, get_course_detail_for_instructor,
    update_course_for_instructor, delete_course_for_instructor, get_existing_doc_by_source_id,
    get_request_lang, upload_course_image, list_course_images, get_course_image_path, delete_course_image,
    get_app_config_and_libary_available, parse_course_markdown,
    CourseMarkdownStructureError, get_doc_by_derivation, save_doc_to_db, get_embeddings_from_db,
    course_upload_job_manager, get_course_generation_count_defaults, validate_course_generation_counts
)
from app.database import get_db
from app.utils import compute_sha256, canonical_storage_path, canonical_storage_path_for_ext
from app.schemas import (
    AnswerGradingRequest, CourseUpdateRequest, COMMON_ERROR_RESPONSES,
    CourseUploadResponse, CourseCreateResponse, AnswerGradingResponse,
    InstructorCourseSummary, InstructorCourseDetailsResponse, CourseUpdateResponse,
    CourseImageUploadResponse, CourseImageResponse, CourseUploadJobResponse,
    CourseUploadPdfJobRequest
)
from app.core import PromptManager

logger = logging.getLogger(__name__)

router = APIRouter(responses=COMMON_ERROR_RESPONSES)

COURSE_GENERATION_COUNT_DEFAULTS = get_course_generation_count_defaults()

def build_course_image_response(
    image: Any,
    course_id: int | None = None,
) -> CourseImageResponse:
    """
    Convert DB image model or old image dict into the public API response shape.

    DB/internal names:
    - filename
    - file_size

    Public API names:
    - original_filename
    - size_bytes
    """

    if isinstance(image, dict):
        image_course_id = image.get("course_id") or course_id
        stored_filename = image.get("stored_filename")

        return CourseImageResponse(
            image_id=image.get("image_id"),
            course_id=image_course_id,
            original_filename=(
                image.get("original_filename")
                or image.get("filename")
                or image.get("name")
                or "uploaded-image"
            ),
            stored_filename=stored_filename,
            url=(
                image.get("url")
                or (
                    f"/api/course/{image_course_id}/images/{stored_filename}"
                    if image_course_id and stored_filename
                    else None
                )
            ),
            content_type=image.get("content_type"),
            size_bytes=image.get("size_bytes") or image.get("file_size"),
            uploaded_at=image.get("uploaded_at"),
        )

    image_course_id = getattr(image, "course_id", None) or course_id
    stored_filename = getattr(image, "stored_filename", None)

    return CourseImageResponse(
        image_id=getattr(image, "image_id", None),
        course_id=image_course_id,
        original_filename=(
            getattr(image, "original_filename", None)
            or getattr(image, "filename", None)
            or "uploaded-image"
        ),
        stored_filename=stored_filename,
        url=f"/api/course/{image_course_id}/images/{stored_filename}"
        if image_course_id and stored_filename
        else None,
        content_type=getattr(image, "content_type", None),
        size_bytes=(
            getattr(image, "size_bytes", None)
            or getattr(image, "file_size", None)
        ),
        uploaded_at=getattr(image, "uploaded_at", None),
    )

def build_instructor_course_details_response(result: dict) -> InstructorCourseDetailsResponse:
    course = result.get("course") or {}

    quiz = result.get("quiz")
    if isinstance(quiz, dict):
        quiz_content = quiz.get("content")
    else:
        quiz_content = quiz

    return InstructorCourseDetailsResponse(
        course_id=course.get("course_id"),
        title=course.get("title"),
        summary=course.get("summary"),
        created_at=course.get("created_at"),
        created_by=course.get("created_by"),
        template_markdown=result.get("template_markdown") or course.get("template_markdown"),
        course_json=result.get("course_json") or course.get("course_json"),
        quiz=quiz_content,
        questions=result.get("questions") or [],
    )

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

def _validate_pdf_generation_counts_or_422(
    qa_count: int,
    quiz_question_count: int,
    quiz_option_count: int,
    misconception_count: int,
) -> dict[str, int]:
    try:
        return validate_course_generation_counts(
            qa_count=qa_count,
            quiz_question_count=quiz_question_count,
            quiz_option_count=quiz_option_count,
            misconception_count=misconception_count,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{exc} for PDF uploads.",
        ) from exc


@router.post(
    "/upload_course_document_pdf_job",
    response_model=CourseUploadJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_course_document_pdf_job(
    payload: Annotated[CourseUploadPdfJobRequest, File()],
    user=Depends(require_role(["Instructor"])),
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db),
):
    file = payload.file
    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"❌ Uploaded file {file.filename} is empty.",
        )

    filename_lower = (file.filename or "").lower()
    if not filename_lower.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="❌ This endpoint only supports PDF uploads.",
        )

    counts = _validate_pdf_generation_counts_or_422(
        payload.qa_count,
        payload.quiz_question_count,
        payload.quiz_option_count,
        payload.misconception_count,
    )

    user_profile = await get_user_profile_by_email(user["email"], db)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="❌ User not found",
        )

    job = await course_upload_job_manager.start_pdf_job(
        user_id=user_profile.user_id,
        file_name=file.filename or "uploaded.pdf",
        file_bytes=contents,
        embedding_model_name=payload.embedding_model_name,
        llm_model_name=payload.llm_model_name,
        response_language=response_language,
        qa_count=counts["qa_count"],
        quiz_question_count=counts["quiz_question_count"],
        quiz_option_count=counts["quiz_option_count"],
        misconception_count=counts["misconception_count"],
    )

    return job.snapshot()


@router.get(
    "/upload_course_document_pdf_job/{job_id}",
    response_model=CourseUploadJobResponse,
)
async def get_upload_course_document_pdf_job(
    job_id: str,
    user=Depends(require_role(["Instructor"])),
    db: AsyncSession = Depends(get_db),
):
    user_profile = await get_user_profile_by_email(user["email"], db)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="❌ User not found",
        )

    job = await course_upload_job_manager.get_job(job_id, user_profile.user_id)
    return job.snapshot()


@router.post(
    "/upload_course_document_pdf_job/{job_id}/cancel",
    response_model=CourseUploadJobResponse,
)
async def cancel_upload_course_document_pdf_job(
    job_id: str,
    user=Depends(require_role(["Instructor"])),
    db: AsyncSession = Depends(get_db),
):
    user_profile = await get_user_profile_by_email(user["email"], db)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="❌ User not found",
        )

    job = await course_upload_job_manager.cancel_job(job_id, user_profile.user_id)
    return job.snapshot()

@router.post("/upload_course_document", 
    response_model=CourseUploadResponse,
    operation_id="upload_course_document")
async def upload_course_document(
    file: UploadFile = File(...),
    embedding_model_name: str = Form(...),
    llm_model_name: str = Form(...),
    qa_count: int = Form(COURSE_GENERATION_COUNT_DEFAULTS["qa_count"]),
    quiz_question_count: int = Form(COURSE_GENERATION_COUNT_DEFAULTS["quiz_question_count"]),
    quiz_option_count: int = Form(COURSE_GENERATION_COUNT_DEFAULTS["quiz_option_count"]),
    misconception_count: int = Form(COURSE_GENERATION_COUNT_DEFAULTS["misconception_count"]),
    replace_existing: bool = Form(False),
    user=Depends(require_role(["Instructor"])),
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db)
) -> CourseUploadResponse:
    """
    Upload and process a course document for instructor course creation.
    If the document is already processed, notify the user. Otherwise, process, store, and generate summary/QA.
    """
    try:
        logger.info(
            "ℹ️ upload_course_document API: "
            f"llm:{llm_model_name}, embedding:{embedding_model_name}, lang:{response_language}, "
            f"qa_count:{qa_count}, "
            f"quiz_questions:{quiz_question_count}, quiz_options:{quiz_option_count}, "
            f"misconceptions:{misconception_count}"
        )
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"❌ Uploaded file {file.filename} is empty.")

        filename_lower = (file.filename or "").lower()
        is_markdown = filename_lower.endswith(".md") or filename_lower.endswith(".markdown")

        if not is_markdown:
            counts = _validate_pdf_generation_counts_or_422(
                qa_count,
                quiz_question_count,
                quiz_option_count,
                misconception_count,
            )
            qa_count = counts["qa_count"]
            quiz_question_count = counts["quiz_question_count"]
            quiz_option_count = counts["quiz_option_count"]
            misconception_count = counts["misconception_count"]

        user_profile = await _get_current_user_profile(user, db)
        
        if is_markdown:
            text_content = contents.decode("utf-8", errors="ignore")
            try:
                parsed_preview = parse_course_markdown(text_content)
            except CourseMarkdownStructureError as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=str(exc),
                ) from exc
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"❌ Invalid markdown structure: {exc}",
                ) from exc

            metadata_preview = parsed_preview.get("metadata") or {}
            course_meta_preview = metadata_preview.get("course") or {}
            source_id = course_meta_preview.get("id")

            existing_doc_by_id = None
            if source_id:
                existing_doc_by_id = await get_existing_doc_by_source_id(
                    source_id,
                    user_profile.user_id,
                    db,
                )

            if existing_doc_by_id and not replace_existing:
                uploaded_at = existing_doc_by_id.uploaded_at
                uploaded_at_iso = (
                    uploaded_at.isoformat() if isinstance(uploaded_at, datetime) else None
                )
                detail_msg = (
                    f"ℹ️ An existing document '{existing_doc_by_id.file_name}' already uses "
                    f"course id '{source_id}'. Uploading will replace its stored content."
                )
                
                logger.info(f"ℹ️ Course upload API: {detail_msg}")

                return CourseUploadResponse(
                    message="markdown_exists",
                    detail=detail_msg,
                    metadata=metadata_preview,
                    existing_document={
                        "document_id": existing_doc_by_id.document_id,
                        "file_name": existing_doc_by_id.file_name,
                        "uploaded_at": uploaded_at_iso,
                    },
                )

            content_hash = compute_sha256(contents)
            storage_path = canonical_storage_path_for_ext(content_hash, "md")

            if not os.path.exists(storage_path):
                os.makedirs(os.path.dirname(storage_path), exist_ok=True)
                with open(storage_path, "wb") as f:
                    f.write(contents)

            docs = await get_doc_by_hash_name(content_hash, user_profile.user_id, db)
            if docs:
                replacing_same_document = (
                    replace_existing
                    and existing_doc_by_id
                    and docs.document_id == existing_doc_by_id.document_id
                )
                if not replacing_same_document:
                    return CourseUploadResponse(
                        message="file_exists",
                        detail=f"File '{file.filename}' is already processed.",
                    )
            
            processed_data = await process_markdown(
                file.filename,
                content_hash,
                storage_path,
                user_profile.user_id,
                db,
            )

            if (
                not processed_data
                or "chunks" not in processed_data
                or len(processed_data["chunks"]) == 0
            ):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="❌ No data extracted from the markdown file.",
                )

            embeddings = await generate_document_embeddings(
                processed_data["chunks"],
                model_name=embedding_model_name,
            )
            if embeddings is None or not isinstance(embeddings, list) or len(embeddings) == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="❌ Failed to generate embeddings. Please check embedding model configuration.",
                )

            docs = await get_doc_by_hash_name(content_hash, user_profile.user_id, db)
            if not docs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="❌ Document not stored correctly in DB.",
                )

            await store_embeddings_to_db(
                processed_data["chunks"],
                processed_data["metadatas"],
                embeddings,
                embedding_model_name=embedding_model_name,
                doc_id=docs.document_id,
                user_id=user_profile.user_id,
                db=db,
            )

            return CourseUploadResponse(
                message="success",
                final_summary=processed_data.get("summary"),
                questions=processed_data.get("questions_dict"),
                quiz=processed_data.get("quiz"),
                metadata=processed_data.get("doc_metadata"),
                template_markdown=processed_data.get("template_markdown"),
                course_json=processed_data.get("course_json"),
            )

        # -----------------------------
        # PDF flow -> generate markdown -> process as markdown
        # -----------------------------
        configs = await get_app_config_and_libary_available(db=db)
        if not configs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")

        prompt_mgr = PromptManager(configs)
        processor = AsyncBatchProcessor(
            prompt_mgr,
            llm_model_name=llm_model_name,
            response_language=response_language,
        )

        content_hash = compute_sha256(contents)
        storage_path = canonical_storage_path(content_hash)

        if not os.path.exists(storage_path):
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            with open(storage_path, "wb") as f:
                f.write(contents)

        pdf_doc = await get_doc_by_hash_name(content_hash, user_profile.user_id, db)
        if pdf_doc:
            return CourseUploadResponse(
                message="file_exists",
                detail=f"File '{file.filename}' is already processed.",
            )

        pdf_doc = await save_doc_to_db(
            file.filename,
            content_hash,
            storage_path,
            user_profile.user_id,
            "processed",
            None,
            None,
            None,
            db,
        )

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
            user_id=user_profile.user_id,
            db=db,
        )

        if linked_markdown_doc:
            existing_embeddings = await get_embeddings_from_db(
                content_hash=linked_markdown_doc.content_hash,
                embedding_model=embedding_model_name,
                user_id=user_profile.user_id,
                db=db,
            )

            processed_markdown_data = await process_markdown(
                linked_markdown_doc.file_name,
                linked_markdown_doc.content_hash,
                linked_markdown_doc.storage_path,
                user_profile.user_id,
                db,
                skip_persistence=True,
                existing_doc_id=linked_markdown_doc.document_id,
            )

            if not existing_embeddings:
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
                    user_id=user_profile.user_id,
                    db=db,
                )

            return CourseUploadResponse(
                message="success",
                final_summary=processed_markdown_data.get("summary"),
                questions=processed_markdown_data.get("questions_dict"),
                quiz=processed_markdown_data.get("quiz"),
                generated_markdown=linked_markdown_doc.doc_content,
                generated_markdown_file_name=linked_markdown_doc.file_name,
                metadata=processed_markdown_data.get("doc_metadata"),
                template_markdown=processed_markdown_data.get("template_markdown"),
                course_json=processed_markdown_data.get("course_json")
            )

        course_data = await processor.summarize_document(
            storage_path,
            qa_count=qa_count,
            quiz_question_count=quiz_question_count,
            quiz_option_count=quiz_option_count,
            misconception_count=misconception_count,
        )

        generated_markdown = course_data.get("generated_markdown")
        if not isinstance(generated_markdown, str) or not generated_markdown.strip():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="❌ Generated markdown is empty.",
            )

        generated_markdown_bytes = generated_markdown.encode("utf-8")
        generated_markdown_hash = compute_sha256(generated_markdown_bytes)
        generated_markdown_path = canonical_storage_path_for_ext(generated_markdown_hash, "md")
        generated_markdown_file_name = course_data.get("generated_markdown_file_name") or "generated-course.md"

        if not os.path.exists(generated_markdown_path):
            os.makedirs(os.path.dirname(generated_markdown_path), exist_ok=True)
            with open(generated_markdown_path, "wb") as generated_file:
                generated_file.write(generated_markdown_bytes)

        processed_markdown_data = await process_markdown(
            generated_markdown_file_name,
            generated_markdown_hash,
            generated_markdown_path,
            user_profile.user_id,
            db,
            source_document_id=pdf_doc.document_id,
            derivation_type="course_markdown",
            generation_config_hash=generation_config_hash,
        )

        if (
            not processed_markdown_data
            or "chunks" not in processed_markdown_data
            or len(processed_markdown_data["chunks"]) == 0
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
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
                detail="❌ Failed to generate embeddings for generated markdown. Please check embedding model configuration.",
            )

        markdown_doc = await get_doc_by_hash_name(
            generated_markdown_hash,
            user_profile.user_id,
            db,
        )
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
            user_id=user_profile.user_id,
            db=db,
        )

        return CourseUploadResponse(
            message="success",
            final_summary=processed_markdown_data.get("summary"),
            questions=processed_markdown_data.get("questions_dict"),
            quiz=processed_markdown_data.get("quiz"),
            generated_markdown=generated_markdown,
            generated_markdown_file_name=generated_markdown_file_name,
            metadata=processed_markdown_data.get("doc_metadata"),
            template_markdown=processed_markdown_data.get("template_markdown"),
            course_json=processed_markdown_data.get("course_json"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error in upload_course_document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@router.post(
    "/create_course_with_summary_and_qas",
    response_model=CourseCreateResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_course_from_generated_content"
)
async def create_course_with_summary_and_qas(
    title: str = Form(...),
    summary: str = Form(...),
    questions: str = Form(...),  # JSON stringified list of dicts
    quiz: str | None = Form(None),
    template_markdown: str | None = Form(None),
    course_json: str | None = Form(None),
    user=Depends(require_role(["Instructor"])),
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db)
) -> CourseCreateResponse:
    """
    Create a new course with a summary and associated questions.
    """
    logger.info(f"ℹ️ Creating course summary of title {title} and {response_language}")
    
    user_profile = await _get_current_user_profile(user, db)
    
    try:
        questions_list = json.loads(questions)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="❌ Invalid questions format"
        )
    
    parsed_course_json = None
    if course_json:
        try:
            parsed_course_json = json.loads(course_json)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="❌ Invalid course_json format",
            )

    result =await create_course_with_summary_and_qas_for_instructor(
        title=title,
        summary=summary,
        questions=questions_list,
        user_id=user_profile.user_id,
        db=db,
        quiz=quiz,
        template_markdown=template_markdown,
        course_json=parsed_course_json,
    )

    logger.info(f"✅ Course created with ID: {result.get('course_id')} for instructor ID: {user_profile.user_id}")
    
    return CourseCreateResponse.model_validate(result)

@router.post(
    "/answer_grading",
    response_model=AnswerGradingResponse,
    operation_id="grade_answer"
)
async def answer_grading(
    payload: AnswerGradingRequest,
    user=Depends(require_role(["Learner", "Instructor","Admin"])),
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db)
) -> AnswerGradingResponse:
    """
    Grade a user's answer against a reference answer.
    """

    question = (payload.question or "").strip()
    reference_answer = (payload.reference_answer or "").strip()
    user_answer = (payload.user_answer or "").strip()
    misconceptions = [
        item.strip()
        for item in (payload.misconceptions or [])
        if isinstance(item, str) and item.strip()
    ]

    user_id = user.get("user_id", "unknown") if isinstance(user, dict) else "unknown"

    logger.info(
        "ℹ️ answer_grading API called. user_id=%s language=%s question_chars=%s answer_chars=%s misconception_count=%s",
        user_id,
        response_language,
        len(question),
        len(user_answer),
        len(misconceptions),
    )

    configs = await get_app_config_and_libary_available(db=db)
    
    if not configs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ Application configurations not found")
    
    reasoning_model_name = payload.reasoning_model_name or configs.get("app_config").default_reasoning_model
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="❌ Question is required",
        )
    if not reference_answer:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="❌ Reference answer is required",
        )
    if not user_answer:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="❌ User answer is required",
        )
    if not reasoning_model_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="❌ reasoning_model_name is required",
        )
    
    graded_response = await grade_user_answer(
        question=question,
        user_answer=user_answer,
        inference_model_name=reasoning_model_name,
        reference_answer=reference_answer,
        misconceptions=misconceptions,
        no_max_tokens=1536,
        response_language=response_language,
    )

    response = AnswerGradingResponse(
        message="success",
        grade=graded_response["grade"],
        summary=graded_response["summary"],
        misconceptions_considered=misconceptions,
    )

    logger.info(
        "✅ answer_grading completed. user_id=%s grade=%s misconception_count=%s",
        user_id,
        response.grade,
        len(misconceptions),
    )

    return response

@router.get(
    "/my_courses",
    response_model=list[InstructorCourseSummary],
    operation_id="list_instructor_courses"
)
async def list_my_courses(
    user=Depends(require_role(["Instructor"])),
    db: AsyncSession = Depends(get_db)
) -> list[InstructorCourseSummary]:
    """
    List all courses created by the authenticated instructor.
    Returns minimal info plus question counts for convenience.
    For new instructors, automatically creates template courses.
    """
    logger.info("ℹ️ Listing courses for instructor.")

    user_profile = await _get_current_user_profile(user, db)
    
    courses = await list_courses_for_instructor(user_profile.user_id, db)

    logger.info(f"✅ Found {len(courses)} courses for instructor ID: {user_profile.user_id}")
    
    return [
        InstructorCourseSummary.model_validate(course)
        for course in courses
    ]

@router.get(
    "/{course_id}",
    response_model=InstructorCourseDetailsResponse,
    operation_id="get_instructor_course_details"
)
async def get_course_detail(
    course_id: int = Path(..., gt=0),
    user=Depends(require_role(["Instructor"])),
    db: AsyncSession = Depends(get_db)
) -> InstructorCourseDetailsResponse:
    """
    Get details for a single course (owned by the instructor) including questions.
    """
    logger.info(f"ℹ️ Fetching details for course ID: {course_id} for instructor.")

    user_profile = await _get_current_user_profile(user, db)
    
    result = await get_course_detail_for_instructor(course_id, user_profile.user_id, db)

    logger.info(f"✅ Retrieved details for course ID: {course_id} for instructor ID: {user_profile.user_id}")
    
    return build_instructor_course_details_response(result)

@router.put(
    "/{course_id}",
    response_model=CourseUpdateResponse,
    operation_id="update_instructor_course"
)
async def update_course(
    course_id: int = Path(..., gt=0),
    payload: CourseUpdateRequest = Body(...),
    user=Depends(require_role(["Instructor"])),
    db: AsyncSession = Depends(get_db)
) -> CourseUpdateResponse:
    """
    Update an instructor-owned course.
    
    Payload fields:
    - title?: str
    - summary?: str
    - quiz?: str | None
    - template_markdown?: str | None
    - course_json?: dict | None
    - questions?: List[{question_id?: int, text: str, answer_text: str}]
    """
    logger.info(f"ℹ️ Updating course ID: {course_id} for instructor with data: {payload}")
    
    user_profile = await _get_current_user_profile(user, db)
    
    result = await update_course_for_instructor(
        course_id,
        user_profile.user_id, 
        payload.model_dump(exclude_unset=True), 
        db
    )
    
    updated_details = build_instructor_course_details_response(result)

    logger.info(
        f"✅ Course updated with ID: {course_id} "
        f"for instructor ID: {user_profile.user_id}"
    )

    return CourseUpdateResponse(
        **updated_details.model_dump(),
        message="success",
    )

@router.delete(
    "/{course_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_instructor_course"
)
async def delete_course(
    course_id: int = Path(..., gt=0),
    user=Depends(require_role(["Instructor"])),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete a course owned by instructor, along with dependent records to avoid FK conflicts.
    """
    logger.info(f"ℹ️ Deleting course ID: {course_id} for instructor.")
    
    user_profile = await _get_current_user_profile(user, db)

    await delete_course_for_instructor(course_id, user_profile.user_id, db)
    
    logger.info(f"✅ Course deleted with ID: {course_id} for instructor ID: {user_profile.user_id}")
    
    return None

# ============================================================
# Course Image Management Endpoints
# ============================================================

@router.post(
    "/{course_id}/images",
    response_model=CourseImageUploadResponse,
    operation_id="upload_course_image"
)
async def upload_image(
    course_id: int = Path(..., gt=0),
    file: UploadFile = File(...),
    user=Depends(require_role(["Instructor"])),
    db: AsyncSession = Depends(get_db)
) -> CourseImageUploadResponse:
    """
    Upload an image for a course.
    Only the course owner (instructor) can upload images.
    """
    
    logger.info(f"ℹ️ Uploading image for course ID: {course_id} for instructor.")

    user_profile = await _get_current_user_profile(user, db)
    
    result = await upload_course_image(course_id, user_profile.user_id, file, db)

    logger.info(f"✅ Image uploaded for course ID: {course_id} for instructor ID: {user_profile.user_id}, image filename: {result.get('original_filename')}")
    
    image_response = build_course_image_response(result, course_id=course_id)

    return CourseImageUploadResponse(
        **image_response.model_dump(),
        message="success",
    )

@router.get(
    "/{course_id}/images",
    response_model=list[CourseImageResponse],
    operation_id="list_course_images"
)
async def list_images(
    course_id: int = Path(..., gt=0),
    user=Depends(require_role(["Instructor"])),
    db: AsyncSession = Depends(get_db)
) -> list[CourseImageResponse]:
    """
    List all images for a course.
    Only the course owner (instructor) can list images.
    """
    logger.info(f"ℹ️ Listing images for course ID: {course_id} for instructor.")
    
    user_profile = await _get_current_user_profile(user, db)
    
    images = await list_course_images(course_id, user_profile.user_id, db)
    
    logger.info(f"✅ Retrieved images for course ID: {course_id} for instructor ID: {user_profile.user_id}")

    return [
        build_course_image_response(image, course_id=course_id)
        for image in images
    ]

@router.get(
    "/{course_id}/images/{image_filename}",
    response_class=FileResponse,
    operation_id="get_course_image"
)
async def get_image(
    course_id: int = Path(..., gt=0),
    image_filename: str = Path(...),
    user=Depends(require_role(["Instructor", "Learner"])),
    db: AsyncSession = Depends(get_db)
) -> FileResponse:
    """
    Retrieve an image file for a course.
    Both instructors and learners can view images.
    Accepts either the original filename or stored_filename (UUID).
    """
    logger.info(f"ℹ️ Fetching image '{image_filename}' for course ID: {course_id} for user.")

    user_profile = await _get_current_user_profile(user, db)
    
    file_path, content_type = await get_course_image_path(
        course_id, image_filename, user_profile.user_id, db
    )

    logger.info(f"✅ Found image path for '{image_filename}' for course ID: {course_id} for user ID: {user_profile.user_id}")
    
    return FileResponse(
        file_path,
        media_type=content_type,
        headers={
            "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
            "Content-Disposition": f"inline; filename={image_filename}"
        }
    )

@router.delete(
    "/{course_id}/images/{stored_filename}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_course_image"
)
async def delete_image(
    course_id: int = Path(..., gt=0),
    stored_filename: str = Path(...),
    user=Depends(require_role(["Instructor"])),
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete an image from a course.
    Only the course owner (instructor) can delete images.
    """
    logger.info(f"ℹ️ Deleting image '{stored_filename}' for course ID: {course_id} for instructor.")
    
    user_profile = await _get_current_user_profile(user, db)
    
    await delete_course_image(course_id, stored_filename, user_profile.user_id, db)

    logger.info(f"✅ Image '{stored_filename}' deleted for course ID: {course_id} for instructor ID: {user_profile.user_id}")
    
    return None
