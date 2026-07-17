import os, fitz, logging
from fastapi import APIRouter, Depends, HTTPException, Response, status
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

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{content_hash}/download")
async def download_pdf(
    content_hash: str,
    user=Depends(require_role(["Learner", "Instructor", "Admin"])), 
    db: AsyncSession = Depends(get_db)
):
    """
    Download a PDF document by its ID.
    This endpoint retrieves a PDF document by its ID and returns it as a file response.
    If the document does not exist or the file path is invalid, it raises a HTTP_404_NOT_FOUND error.
    """
    print(f"ℹ️ Downloading PDF document with content_hash: {content_hash}")
    if not content_hash:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "❌ content_hash is required.")
    
    if not isinstance(content_hash, str):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "❌ content_hash must be an String.")
    
    user_profile = await get_user_profile_by_email(user["email"], db)
    
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")
    
    # Fetch the document from the database 
    doc = await get_doc_by_hash_name(content_hash, user_profile.user_id, db)

    if not doc or not doc.storage_path or not os.path.exists(doc.storage_path):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "❌ file not found")
    
    print(f"✅ Found document: {doc.file_name} at {doc.storage_path}")
    
    response = FileResponse(
        doc.storage_path, 
        media_type="application/octet-stream", 
        filename=doc.file_name
    )
    
    print(f"✅ Returning file response for document: {response}")
    
    return response

@router.get("/{content_hash}/page/{page}.png")
async def render_page_png(
    content_hash: str, 
    page: int,
    user=Depends(require_role(["Learner", "Instructor", "Admin"])), 
    db: AsyncSession = Depends(get_db)
):
    """
    Render a specific page of a PDF document as a PNG image.
    This endpoint retrieves a specific page of a PDF document by its ID and page number,
    and returns it as a PNG image response.
    If the document does not exist, the file path is invalid, or the page number is out of range,
    it raises a HTTP_404_NOT_FOUND error.
    """
    print(f"ℹ️ Rendering page {page} of document with ID: {content_hash}")
    if not content_hash or not page:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "❌ content_hash and page number are required")
    
    if not isinstance(content_hash, str) or not isinstance(page, int):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "❌ content_hash should be String and page number must be integer.")
    
    if page < 1:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "❌ Page number must be greater than 0")
    
    user_profile = await get_user_profile_by_email(user["email"], db)
    
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")
    
    # Fetch the document by content hash and user ID
    doc = await get_doc_by_hash_name(content_hash, user_profile.user_id, db)
    
    if not doc or not doc.storage_path or not os.path.exists(doc.storage_path):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "❌ file not found")
    
    print(f"✅ Found document: {doc.file_name} at {doc.storage_path}")

    # Open the PDF and render the specified page as a PNG image
    print(f"ℹ️ Opening PDF document: {doc.storage_path} to render page {page}")
    
    pdf = fitz.open(doc.storage_path)
    
    if page < 1 or page > len(pdf):
        pdf.close()
        raise HTTPException(status.HTTP_404_NOT_FOUND, "❌ page out of range")

    pix = pdf[page-1].get_pixmap(matrix=fitz.Matrix(2, 2))  # retina-ish preview
    pdf.close()

    if not pix:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "❌ Failed to render page as image")
    
    response = Response(pix.tobytes("png"), media_type="image/png")

    print(f"✅ Rendered page {page} of document {content_hash} as PNG image {response}.")

    return response

@router.get("/{content_hash}/preview.png")
async def render_full_preview_png(
    content_hash: str,
    # Optional controls
    page_from: int = 1,
    page_to: Optional[int] = None,      # None => all pages
    scale: float = 2.0,                  # 1.0 ~ 72 dpi; 2.0 ~ ~144 dpi
    gap_px: int = 8,                     # spacing between pages
    max_pixels: int = 50_000_000,        # guardrail (~50MP)
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Stitch pages (PDF only) into ONE tall PNG for quick full-document preview.
    Use query params to limit range/scale. Raises 413 if image would be too large.
    """
    if scale <= 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "❌ scale must be > 0")
    if page_from < 1:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "❌ page_from must be >= 1")

    user_profile = await get_user_profile_by_email(user["email"], db)

    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")

    doc = await get_doc_by_hash_name(content_hash, user_profile.user_id, db)

    if not doc or not doc.storage_path or not os.path.exists(doc.storage_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ file not found")

    lower_path = doc.storage_path.lower()

    if lower_path.endswith(".pdf"):
        pdf = fitz.open(doc.storage_path)

        try:
            total_pages = len(pdf)
            last = page_to if page_to is not None else total_pages

            if last < page_from or page_from > total_pages:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "❌ page range out of bounds")

            last = min(last, total_pages)

            matrix = fitz.Matrix(scale, scale)
            pil_pages: list[Image.Image] = []

            # Render each page -> PIL image
            for i in range(page_from - 1, last):
                pix = pdf[i].get_pixmap(matrix=matrix)
                mode = "RGBA" if pix.alpha else "RGB"
                img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)

                if img.mode != "RGB":
                    img = img.convert("RGB")
                pil_pages.append(img)

            if not pil_pages:
                raise HTTPException(status.HTTP_404_NOT_FOUND, "❌ no pages rendered")

            # Compute stitched canvas size (vertical)
            width = max(p.width for p in pil_pages)
            height = sum(p.height for p in pil_pages) + gap_px * (len(pil_pages) - 1)

            # Guardrail for extremely long outputs
            if width * height > max_pixels:
                raise HTTPException(status_code=413, detail="❌ Preview too large to render as a single PNG")

            canvas = Image.new("RGB", (width, height), (255, 255, 255))  # type: ignore[arg-type]
            y = 0
            for p in pil_pages:
                # center page horizontally
                x = (width - p.width) // 2
                canvas.paste(p, (x, y))
                y += p.height + gap_px

            buf = BytesIO()
            canvas.save(buf, format="PNG", optimize=True)
            buf.seek(0)
            return Response(buf.getvalue(), media_type="image/png")
        finally:
            pdf.close()

    raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="❌ Preview PNG only supported for PDF files")


@router.get("/{content_hash}/markdown")
async def render_markdown_content(
    content_hash: str,
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Return markdown document content and metadata for preview."""

    if not content_hash:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "content_hash is required.")

    user_profile = await get_user_profile_by_email(user["email"], db)

    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")

    doc = await get_doc_by_hash_name(content_hash, user_profile.user_id, db)

    if not doc or not doc.storage_path or not os.path.exists(doc.storage_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ file not found")

    if not doc.storage_path.lower().endswith((".md", ".markdown")):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="❌ Markdown preview only available for markdown files")

    # Prefer stored combined content; fall back to raw file on disk.
    stored_content = doc.doc_content or ""
    raw_markdown = stored_content

    if not stored_content:
        try:
            with open(doc.storage_path, "r", encoding="utf-8") as handle:
                raw_markdown = handle.read()
                stored_content = raw_markdown
        except Exception as exc:
            logger.warning("Failed to read markdown file %s: %s", doc.storage_path, exc)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="❌ Unable to load markdown content") from exc
    else:
        # We still want the raw markdown for quiz/Q&A parsing if doc_content stripped sections.
        try:
            with open(doc.storage_path, "r", encoding="utf-8") as handle:
                raw_markdown = handle.read()
        except Exception as exc:
            logger.info("Could not read original markdown for %s; continuing with stored content. Error: %s", doc.storage_path, exc)
            raw_markdown = stored_content

    quiz_dict = None
    questions = []
    quiz_yaml = None
    summary = None
    parsed_metadata = None

    try:
        parsed = parse_structured_markdown(raw_markdown)
    except (MarkdownStructureError, ValueError) as exc:
        logger.info("Markdown preview parse skipped for %s: %s", doc.file_name, exc)
        parsed = None
    except Exception as exc:
        logger.warning("Unexpected error parsing markdown preview for %s: %s", doc.file_name, exc)
        raise

    if parsed:
        parsed_metadata = parsed.get("metadata")
        summary = parsed.get("summary")
        quiz_dict = parsed.get("quiz_dict")
        quiz_yaml = parsed.get("quiz_yaml_str")
        questions = parsed.get("questions_dict", {}).get("qa_list", []) or []
        # Prefer structured content as display body when available.
        structured_content = parsed.get("content")
        if structured_content:
            stored_content = structured_content

    response_metadata = doc.doc_metadata or {}
    if parsed_metadata:
        response_metadata = {**parsed_metadata, **response_metadata}

    return {
        "file_name": doc.file_name,
        "content": stored_content,
        "metadata": response_metadata,
        "summary": summary,
        "quiz": quiz_dict,
        "quiz_yaml": quiz_yaml,
        "questions": questions,
        "raw_markdown": raw_markdown,
    }
