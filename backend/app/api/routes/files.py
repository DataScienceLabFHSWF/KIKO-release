# backend/app/api/routes/files.py

import os, fitz, logging
from fastapi import APIRouter, Depends, HTTPException, Response, status, Path, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import (
    require_role, get_user_profile_by_email, get_doc_by_hash_name, 
    parse_structured_markdown, MarkdownStructureError
)
from typing import Optional
from PIL import Image
from io import BytesIO
from app.schemas import (
    COMMON_ERROR_RESPONSES, MarkdownPreviewResponse, ApiErrorResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(responses=COMMON_ERROR_RESPONSES)

SHA256_PATTERN = r"^[a-fA-F0-9]{64}$"

async def _get_owned_document(
    content_hash: str,
    user: dict,
    db: AsyncSession,
):
    """
    Helper function to retrieve a document by content hash that belongs to the current user.
    This function checks if the document with the given content hash exists and is owned by the current user.
    If the document does not exist or is not owned by the user, it raises a HTTP_404_NOT_FOUND error. 
    This ensures that users can only access their own documents.
    """
    user_profile = await get_user_profile_by_email(user["email"], db)

    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    doc = await get_doc_by_hash_name(
        content_hash,
        user_profile.user_id,
        db,
    )

    if not doc or not doc.storage_path or not os.path.exists(doc.storage_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found.",
        )

    return doc

@router.get(
    "/{content_hash}/download",
    response_class=FileResponse,
    operation_id="download_file",
    responses={
        200: {
            "description": "Document file download",
            "content": {
                "application/octet-stream": {},
                "application/pdf": {},
                "text/markdown": {},
            },
        }
    },
)
async def download_file(
    content_hash: str = Path(..., pattern=SHA256_PATTERN),
    user=Depends(require_role(["Learner", "Instructor", "Admin"])), 
    db: AsyncSession = Depends(get_db)
):
    """
    Download a file by its content hash.
    This endpoint retrieves a file by its content hash and returns it as a file response.
    If the file does not exist or the file path is invalid, it raises a HTTP_404_NOT_FOUND error.
    """
    logger.info(f"ℹ️ Downloading file with content_hash: {content_hash}")
    
    doc = await _get_owned_document(content_hash, user, db)
    
    response = FileResponse(
        path=doc.storage_path,
        media_type="application/octet-stream",
        filename=doc.file_name,
    )
    
    logger.info(f"✅ Returning file response for document: {response}")
    
    return response

@router.get(
    "/{content_hash}/page/{page}.png",
    response_class=Response,
    operation_id="render_file_page_png",
    responses={
        200: {
            "description": "Rendered PDF page as PNG",
            "content": {"image/png": {}},
        }
    },
)
async def render_page_png(
    content_hash: str = Path(..., pattern=SHA256_PATTERN), 
    page: int = Path(..., gt=0),
    user=Depends(require_role(["Learner", "Instructor", "Admin"])), 
    db: AsyncSession = Depends(get_db)
) -> Response:
    """
    Render a specific page of a PDF document as a PNG image.
    This endpoint retrieves a specific page of a PDF document by its ID and page number,
    and returns it as a PNG image response.
    If the document does not exist, the file path is invalid, or the page number is out of range,
    it raises a HTTP_404_NOT_FOUND error.
    """
    logger.info(f"ℹ️ Rendering page {page} of document with ID: {content_hash}")
    
    doc = await _get_owned_document(content_hash, user, db)
    
    if not doc.storage_path.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Page rendering is only supported for PDF files.",
        )
    
    try:
        pdf = fitz.open(doc.storage_path)
        try:
            if page > len(pdf):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Page out of range.",
                )

            pix = pdf[page - 1].get_pixmap(matrix=fitz.Matrix(2, 2))

            logger.info(f"✅ Successfully rendered page {page} of document {content_hash} as PNG")
            
            return Response(
                content=pix.tobytes("png"),
                media_type="image/png",
                headers={"Cache-Control": "public, max-age=86400"},
            )
        finally:
            pdf.close()
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("❌ Failed to render PDF page")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Failed to render PDF page.",
        ) from exc

@router.get(
    "/{content_hash}/preview.png",
    response_class=Response,
    operation_id="render_file_preview_png",
    responses={
        200: {
            "description": "Rendered multi-page PDF preview as PNG",
            "content": {"image/png": {}},
        },
        413: {
            "model": ApiErrorResponse,
            "description": "Preview too large",
        },
    },
)
async def render_full_preview_png(
    content_hash: str = Path(..., pattern=SHA256_PATTERN),
    # Optional controls
    page_from: int = Query(1, ge=1),
    page_to: Optional[int] = Query(None, ge=1),      # None => all pages
    scale: float = Query(2.0, gt=0, le=4.0),                  # 1.0 ~ 72 dpi; 2.0 ~ ~144 dpi
    gap_px: int = Query(8, ge=0, le=100),                     # spacing between pages
    max_pixels: int = Query(50_000_000, gt=0),        # guardrail (~50MP)
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Render a multi-page PDF document as a single PNG image for preview.
    This endpoint retrieves a PDF document by its content hash and renders a specified page range as a single PNG image.
    Optional query parameters allow control over the page range, rendering scale, spacing between pages, and maximum allowed image size.
    If the document does not exist, the file path is invalid, the page range is out of bounds, or the resulting image exceeds size limits,
    it raises an appropriate HTTP error.
    """
    logger.info(f"ℹ️ Rendering full PDF preview for document with ID: {content_hash}, page_from: {page_from}, page_to: {page_to}, scale: {scale}, gap_px: {gap_px}, max_pixels: {max_pixels}")
    
    doc = await _get_owned_document(content_hash, user, db)

    if not doc.storage_path.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Preview PNG is only supported for PDF files.",
        )

    try:
        pdf = fitz.open(doc.storage_path)
        try:
            total_pages = len(pdf)
            last = page_to if page_to is not None else total_pages

            if page_from > total_pages or last < page_from:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Page range out of bounds.",
                )

            last = min(last, total_pages)

            matrix = fitz.Matrix(scale, scale)
            pil_pages: list[Image.Image] = []

            for i in range(page_from - 1, last):
                pix = pdf[i].get_pixmap(matrix=matrix)
                mode = "RGBA" if pix.alpha else "RGB"
                img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)

                if img.mode != "RGB":
                    img = img.convert("RGB")

                pil_pages.append(img)

            if not pil_pages:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No pages rendered.",
                )

            width = max(page.width for page in pil_pages)
            height = sum(page.height for page in pil_pages) + gap_px * (len(pil_pages) - 1)

            if width * height > max_pixels:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Preview too large to render as a single PNG.",
                )

            canvas = Image.new("RGB", (width, height), (255, 255, 255))

            y = 0
            for page_img in pil_pages:
                x = (width - page_img.width) // 2
                canvas.paste(page_img, (x, y))
                y += page_img.height + gap_px

            buffer = BytesIO()
            canvas.save(buffer, format="PNG", optimize=True)
            buffer.seek(0)

            logger.info(f"✅ Successfully rendered full PDF preview for document {content_hash} as PNG with dimensions {canvas.width}x{canvas.height} and size {buffer.getbuffer().nbytes} bytes")
            
            return Response(
                content=buffer.getvalue(),
                media_type="image/png",
                headers={"Cache-Control": "public, max-age=86400"},
            )

        finally:
            pdf.close()

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("❌ Failed to render full PDF preview")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Failed to render PDF preview.",
        ) from exc

@router.get(
    "/{content_hash}/markdown",
    response_model=MarkdownPreviewResponse,
    operation_id="get_markdown_preview"
)
async def render_markdown_content(
    content_hash: str = Path(..., pattern=SHA256_PATTERN),
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    db: AsyncSession = Depends(get_db),
) -> MarkdownPreviewResponse:
    """
    Render markdown content for preview.
    This endpoint retrieves a markdown document by its content hash, parses it to extract structured content,
    summary, quiz information, and questions, and returns this information in a structured response.
    If the document does not exist, the file path is invalid, or the content cannot be parsed, it raises an appropriate HTTP error.
    """
    logger.info(f"ℹ️ Rendering markdown preview for document with ID: {content_hash}")
    
    doc = await _get_owned_document(content_hash, user, db)

    if not doc.storage_path.lower().endswith((".md", ".markdown")):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Markdown preview is only available for markdown files.",
        )

    stored_content = doc.doc_content or ""
    raw_markdown = stored_content

    if not stored_content:
        try:
            with open(doc.storage_path, "r", encoding="utf-8") as handle:
                raw_markdown = handle.read()
                stored_content = raw_markdown
        except Exception as exc:
            logger.exception("❌ Unable to load markdown content")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="❌ Unable to load markdown content.",
            ) from exc
    else:
        try:
            with open(doc.storage_path, "r", encoding="utf-8") as handle:
                raw_markdown = handle.read()
        except Exception:
            raw_markdown = stored_content

    quiz_dict = None
    questions: list[dict] = []
    quiz_yaml = None
    summary = None
    parsed_metadata = None

    try:
        parsed = parse_structured_markdown(raw_markdown)
    except (MarkdownStructureError, ValueError) as exc:
        logger.info("ℹ️ Markdown preview parse skipped for %s: %s", doc.file_name, exc)
        parsed = None
    except Exception as exc:
        logger.exception("❌ Unexpected error parsing markdown preview")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Failed to parse markdown preview.",
        ) from exc

    if parsed:
        parsed_metadata = parsed.get("metadata")
        summary = parsed.get("summary")
        quiz_dict = parsed.get("quiz_dict")
        quiz_yaml = parsed.get("quiz_yaml_str")
        questions = parsed.get("questions_dict", {}).get("qa_list", []) or []

        structured_content = parsed.get("content")
        if structured_content:
            stored_content = structured_content

    response_metadata = doc.doc_metadata or {}

    if parsed_metadata:
        response_metadata = {
            **parsed_metadata,
            **response_metadata,
        }
    
    logger.info(f"✅ Successfully rendered markdown preview for document {content_hash} with summary: {summary}, quiz: {quiz_dict}, questions count: {len(questions)}, and metadata: {response_metadata}")
    
    return MarkdownPreviewResponse(
        file_name=doc.file_name,
        content=stored_content,
        metadata=response_metadata,
        summary=summary,
        quiz=quiz_dict,
        quiz_yaml=quiz_yaml,
        questions=questions,
        raw_markdown=raw_markdown,
    )
