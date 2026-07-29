# backend/app/api/routes/course.py
import os, json
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form, Body, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse, FileResponse
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
    course_upload_job_manager,
    get_course_generation_count_defaults,
    validate_course_generation_counts,
)
from app.database import get_db
from app.utils import compute_sha256, canonical_storage_path, canonical_storage_path_for_ext
from app.schemas import (
    CourseUpdateRequest,
    CourseUploadJobResponse,
    CourseUploadPdfJobRequest,
    GradePayload,
)
from app.core import PromptManager

router = APIRouter()

COURSE_GENERATION_COUNT_DEFAULTS = get_course_generation_count_defaults()


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

@router.post("/upload_course_document")
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
):
    """
    Upload and process a course document for instructor course creation.
    If the document is already processed, notify the user. Otherwise, process, store, and generate summary/QA.
    """
    try:
        print(
            "ℹ️ upload_course_document API: "
            f"llm:{llm_model_name}, embedding:{embedding_model_name}, lang:{response_language}, "
            f"qa_count:{qa_count}, "
            f"quiz_questions:{quiz_question_count}, quiz_options:{quiz_option_count}, "
            f"misconceptions:{misconception_count}"
        )
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"❌ Uploaded file {file.filename} is empty.")

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

        user_profile = await get_user_profile_by_email(user["email"], db)
        if not user_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")

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
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "message": "markdown_exists",
                        "detail": detail_msg,
                        "metadata": metadata_preview,
                        "existing_document": {
                            "document_id": existing_doc_by_id.document_id,
                            "file_name": existing_doc_by_id.file_name,
                            "uploaded_at": uploaded_at_iso,
                        },
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
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={
                            "message": "file_exists",
                            "detail": f"ℹ️ File '{file.filename}' is already processed.",
                        },
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

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "success",
                    "final_summary": processed_data.get("summary"),
                    "questions": processed_data.get("questions_dict"),
                    "quiz": processed_data.get("quiz"),
                    "metadata": processed_data.get("doc_metadata"),
                    "template_markdown": processed_data.get("template_markdown"),
                    "course_json": processed_data.get("course_json"),
                },
            )

        # -----------------------------
        # PDF flow -> generate markdown -> process as markdown
        # -----------------------------
        configs = await get_app_config_and_libary_available()
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
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "file_exists",
                    "detail": f"File '{file.filename}' is already processed.",
                },
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

            return JSONResponse(status_code=status.HTTP_200_OK, content={
                "message": "success",
                "final_summary": processed_markdown_data.get("summary"),
                "questions": processed_markdown_data.get("questions_dict"),
                "quiz": processed_markdown_data.get("quiz"),
                "generated_markdown": linked_markdown_doc.doc_content,
                "generated_markdown_file_name": linked_markdown_doc.file_name,
                "metadata": processed_markdown_data.get("doc_metadata"),
                "template_markdown": processed_markdown_data.get("template_markdown"),
                "course_json": processed_markdown_data.get("course_json"),
            })

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

        return JSONResponse(status_code=status.HTTP_200_OK, content={
            "message": "success",
            "final_summary": processed_markdown_data.get("summary"),
            "questions": processed_markdown_data.get("questions_dict"),
            "quiz": processed_markdown_data.get("quiz"),
            "generated_markdown": generated_markdown,
            "generated_markdown_file_name": generated_markdown_file_name,
            "metadata": processed_markdown_data.get("doc_metadata"),
            "template_markdown": processed_markdown_data.get("template_markdown"),
            "course_json": processed_markdown_data.get("course_json"),
        })

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@router.post("/create_course_with_summary_and_qas")
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
):
    """
    Create a new course with a summary and associated questions.
    """
    print(f"ℹ️ Creating course summary of title {title} and {response_language}")
    
    user_profile = await get_user_profile_by_email(user["email"], db)
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="❌ User not found"
        )
    
    try:
        questions_list = json.loads(questions)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
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

    return await create_course_with_summary_and_qas_for_instructor(
        title=title,
        summary=summary,
        questions=questions_list,
        user_id=user_profile.user_id,
        db=db,
        quiz=quiz,
        template_markdown=template_markdown,
        course_json=parsed_course_json,
    )

@router.post("/answer_grading")
async def answer_grading(
    payload: GradePayload,
    user=Depends(require_role(["Learner", "Instructor","Admin"])),
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db)
):
    """
    Grade a user's answer against a reference answer.
    """
    print(f"ℹ️ answer_grading API: {payload} and {response_language}")
    
    question = (payload.question or "").strip()
    reference_answer = (payload.reference_answer or "").strip()
    user_answer = (payload.user_answer or "").strip()
    reasoning_model_name = payload.reasoning_model_name
    
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
        no_max_tokens=1024,
        response_language=response_language,
    )
    
    print(f"ℹ️ Response from answer_grading services: {graded_response}")
    
    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "success",
            "grade": graded_response["grade"],
            "summary": graded_response["summary"]
        }
    )
    print(f"✅ From answer_grading API response: {response}")
    
    return response

@router.get("/my_courses")
async def list_my_courses(
    user=Depends(require_role(["Learner", "Instructor",])),
    db: AsyncSession = Depends(get_db)
):
    """
    List all courses created by the authenticated instructor.
    Returns minimal info plus question counts for convenience.
    For new instructors, automatically creates template courses.
    """
    user_profile = await get_user_profile_by_email(user["email"], db)
    
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    
    return await list_courses_for_instructor(user_profile.user_id, db)

@router.get("/{course_id}")
async def get_course_detail(
    course_id: int = Path(..., gt=0),
    user=Depends(require_role(["Learner", "Instructor"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Get details for a single course (owned by the instructor) including questions.
    """
    user_profile = await get_user_profile_by_email(user["email"], db)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")
    return await get_course_detail_for_instructor(course_id, user_profile.user_id, db)


@router.put("/{course_id}")
async def update_course(
    course_id: int = Path(..., gt=0),
    payload: CourseUpdateRequest = Body(...),
    user=Depends(require_role(["Instructor"])),
    db: AsyncSession = Depends(get_db)
):
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
    
    user_profile = await get_user_profile_by_email(user["email"], db)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")
    
    return await update_course_for_instructor(
        course_id, 
        user_profile.user_id, 
        payload.model_dump(exclude_unset=False), 
        db
    )

@router.delete("/{course_id}")
async def delete_course(
    course_id: int = Path(..., gt=0),
    user=Depends(require_role(["Instructor"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a course owned by instructor, along with dependent records to avoid FK conflicts.
    """
    user_profile = await get_user_profile_by_email(user["email"], db)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")
    return await delete_course_for_instructor(course_id, user_profile.user_id, db)


# ============================================================
# Course Image Management Endpoints
# ============================================================

@router.post("/{course_id}/images")
async def upload_image(
    course_id: int = Path(..., gt=0),
    file: UploadFile = File(...),
    user=Depends(require_role(["Instructor"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload an image for a course.
    Only the course owner (instructor) can upload images.
    """
    user_profile = await get_user_profile_by_email(user["email"], db)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return await upload_course_image(course_id, user_profile.user_id, file, db)


@router.get("/{course_id}/images")
async def list_images(
    course_id: int = Path(..., gt=0),
    user=Depends(require_role(["Instructor"])),
    db: AsyncSession = Depends(get_db)
):
    """
    List all images for a course.
    Only the course owner (instructor) can list images.
    """
    user_profile = await get_user_profile_by_email(user["email"], db)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return await list_course_images(course_id, user_profile.user_id, db)


@router.get("/{course_id}/images/{image_filename}")
async def get_image(
    course_id: int = Path(..., gt=0),
    image_filename: str = Path(...),
    user=Depends(require_role(["Instructor", "Learner"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve an image file for a course.
    Both instructors and learners can view images.
    Accepts either the original filename or stored_filename (UUID).
    """
    user_profile = await get_user_profile_by_email(user["email"], db)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    file_path, content_type = await get_course_image_path(
        course_id, image_filename, user_profile.user_id, db
    )
    
    return FileResponse(
        file_path,
        media_type=content_type,
        headers={
            "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
            "Content-Disposition": f"inline; filename={image_filename}"
        }
    )


@router.delete("/{course_id}/images/{stored_filename}")
async def delete_image(
    course_id: int = Path(..., gt=0),
    stored_filename: str = Path(...),
    user=Depends(require_role(["Instructor"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an image from a course.
    Only the course owner (instructor) can delete images.
    """
    user_profile = await get_user_profile_by_email(user["email"], db)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return await delete_course_image(course_id, stored_filename, user_profile.user_id, db)
