"""
Service for managing template courses that are cloned for new instructors.
"""
# backend/app/services/course_template_manager.py
import json, uuid, shutil
from copy import deepcopy
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import (CourseModel, QuestionModel, QuizModel, CourseImageModel, UserModel)
from .user_service import get_system_user_id
from .course_markdown_parser_service import parse_course_markdown, CourseMarkdownStructureError
from typing import Any, Dict
from app.utils import rewrite_markdown_image_urls
from .default_course_document_service import provision_markdown_document_for_course

# Path to template course markdown files
TEMPLATE_COURSES_DIR = Path("/backend/data/default_courses")

# Path to template images directory
TEMPLATE_IMAGES_DIR = Path("/backend/data/default_images")

# Courses available to ONLY selected instructor (e.g. for testing or special access)
RESTRICTED_TEMPLATE_FILES = ["fusion.md", "smr.md"]

# Courses available to FH-SWF instructors
FHSWF_DEFAULT_TEMPLATE_FILES = ["grundlagen-strahlung-strahlenschutz.md", "nukleare-sicherheit.md", "nukleare-sicherheit-intermediate.md"]

# Courses available to TUM instructors
TUM_DEFAULT_TEMPLATE_FILES = ["grundlagen-strahlung-strahlenschutz.md"]

# Courses available to all instructors by default
EXAMPLE_DEFAULT_TEMPLATE_FILES = ["birds.md", "climate.md"]

def load_template_config() -> dict:
    """
    Load template configuration from JSON file.
    Similar to PromptManager pattern for loading external configuration.
    
    Returns dict mapping template filenames to their image configurations.
    """
    config_path = TEMPLATE_COURSES_DIR / "template_config.json"
    
    if not config_path.exists():
        print(f"❌ Template config not found: {config_path}")
        raise FileNotFoundError(f"Template config not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    print(f"✅ Loaded template configuration from {config_path}")
    return config

def replace_course_id_placeholders(value: Any, course_id: int) -> Any:
    """
    Recursively replace {{COURSE_ID}} placeholders in strings, lists, and dicts.
    """
    if isinstance(value, str):
        return value.replace("{{COURSE_ID}}", str(course_id))
    if isinstance(value, list):
        return [replace_course_id_placeholders(v, course_id) for v in value]
    if isinstance(value, dict):
        return {k: replace_course_id_placeholders(v, course_id) for k, v in value.items()}
    return value

def rewrite_course_json_markdown_fields(course_json: dict, course_id: int) -> tuple[dict, list[str]]:
    """
    Rewrite markdown image URLs inside stored course_json so learner/instructor
    pages can render course images through the course image endpoint.

    Rewrites:
    - overview_md
    - each module.content_md
    - each module.further_reading_md
    """
    rewritten = deepcopy(course_json or {})
    referenced_images: set[str] = set()

    def _rewrite_field(container: dict, field_name: str):
        raw_value = container.get(field_name)
        if isinstance(raw_value, str) and raw_value.strip():
            rewritten_value, refs = rewrite_markdown_image_urls(raw_value, course_id)
            container[field_name] = rewritten_value
            if refs:
                referenced_images.update(refs)

    _rewrite_field(rewritten, "overview_md")

    modules = rewritten.get("modules")
    if isinstance(modules, list):
        for module in modules:
            if isinstance(module, dict):
                _rewrite_field(module, "content_md")
                _rewrite_field(module, "further_reading_md")

    return rewritten, sorted(referenced_images)

def copy_default_images_for_course(course_id: int, template_images: list[dict], user_id: int, db: AsyncSession) -> None:
    """
    Copy default template images to a new course directory and create database entries.
    
    Args:
        course_id: The ID of the newly created course
        template_images: List of dicts with 'filename', 'alt_text' keys
        user_id: The instructor's user ID
        db: Database session
    """
    # Define paths
    course_dir = Path(f"/backend/data/courses/{course_id}/images")
    
    # Create course images directory if it doesn't exist
    course_dir.mkdir(parents=True, exist_ok=True)
    
    for img in template_images:
        try:
            src_file = TEMPLATE_IMAGES_DIR / img["filename"]
            if not src_file.exists():
                print(f"⚠️ Template image not found: {src_file}")
                continue
            
            # Generate unique stored filename using UUID to avoid conflicts
            ext = src_file.suffix  # e.g., '.png', '.gif'
            stored_filename = f"{uuid.uuid4()}{ext}"
            
            # Copy to course directory with unique name
            dest_file = course_dir / stored_filename
            shutil.copy2(src_file, dest_file)
            
            # Get file info
            file_size = dest_file.stat().st_size
            
            # Determine content type
            content_type_map = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
                '.svg': 'image/svg+xml'
            }
            content_type = content_type_map.get(ext.lower(), 'application/octet-stream')
            
            # Create database entry with unique stored_filename
            image_record = CourseImageModel(
                course_id=course_id,
                filename=img["filename"],  # Original name for display
                stored_filename=stored_filename,  # UUID-based unique name
                file_path=str(dest_file),
                content_type=content_type,
                file_size=file_size,
                uploaded_by=user_id
            )
            db.add(image_record)
            
            print(f"✅ Copied template image: {img['filename']} -> {stored_filename} to course {course_id}")
            
        except Exception as e:
            print(f"❌ Error copying template image {img.get('filename', 'unknown')}: {e}")
            continue

def load_template_courses(user_email: str = None):
    """
    Load template courses from NEW markdown templates.

    Uses parse_course_markdown() so template courses are created with the same
    stored structure as instructor-created markdown courses.

    Returns:
        [
          {
            "title": ...,
            "summary": ...,
            "template_markdown": ...,
            "course_json": ...,
            "questions": [{"text": ..., "answer_text": ...}, ...],
            "quiz": "...yaml string...",
            "default_images": [...],
          },
          ...
        ]
    """
    templates: list[dict] = []

    if user_email and user_email.endswith("@fh-swf.de"):
        files_to_load = set(FHSWF_DEFAULT_TEMPLATE_FILES)
    elif user_email and user_email.endswith("@tum.de"):
        files_to_load = set(TUM_DEFAULT_TEMPLATE_FILES)
    elif user_email and user_email.lower() == "thomas.kopinski@gmail.com":
        files_to_load = set(RESTRICTED_TEMPLATE_FILES)
    else:
        files_to_load = set(EXAMPLE_DEFAULT_TEMPLATE_FILES)
    
    # Template course files mapping (filename -> images) - loaded from JSON
    TEMPLATE_FILES = load_template_config()
    
    for filename, config in TEMPLATE_FILES.items():
        if filename not in files_to_load:
            continue

        md_file = TEMPLATE_COURSES_DIR / filename
        if not md_file.exists():
            print(f"⚠️ Template file not found: {md_file}")
            continue

        try:
            content = md_file.read_text(encoding="utf-8")

            parsed = parse_course_markdown(content)

            title = ((parsed.get("course_json") or {}).get("course") or {}).get("title")
            title = (title or filename.replace(".md", "").replace("-", " ").title()).strip()

            questions = [
                {
                    "text": q.get("question", ""),
                    "answer_text": q.get("answer", ""),
                }
                for q in ((parsed.get("questions_dict") or {}).get("qa_list") or [])
                if (q.get("question") or "").strip() and (q.get("answer") or "").strip()
            ]

            templates.append(
                {
                    "source_file_name": filename,
                    "title": title,
                    "summary": parsed.get("summary") or "",
                    "template_markdown": parsed.get("template_markdown") or content,
                    "course_json": parsed.get("course_json") or {},
                    "questions": questions,
                    "quiz": parsed.get("quiz_yaml_str") or "",
                    "default_images": config.get("images", []),
                }
            )
            print(f"✅ Loaded template: {title}")

        except CourseMarkdownStructureError as e:
            print(f"❌ Invalid template markdown structure in {filename}: {e}")
            continue
        except Exception as e:
            print(f"❌ Error loading template {filename}: {e}")
            continue

    return templates

async def create_template_courses_for_instructor(
    user_id: int, 
    db: AsyncSession,
    embedding_model_name: str | None = None,
) -> Dict:
    """
    Create default course clones for a new instructor and also provision
    their markdown documents + embeddings for My Documents and RAG.
    """

    provision_report = {
        "courses_created": 0,
        "documents_created": 0,
        "document_failures": [],
    }

    try:
        user_result = await db.execute(
            select(UserModel).where(UserModel.user_id == user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            print(f"⚠️ User with ID {user_id} not found")
            return provision_report

        if getattr(user, "template_courses_initialized", False):
            return provision_report

        template_courses = load_template_courses(user_email=user.email)

        if not template_courses:
            user.template_courses_initialized = True
            await db.commit()
            return provision_report

        system_user_id = await get_system_user_id(db)
        is_system_template = (user_id == system_user_id) if system_user_id else False

        document_jobs: list[dict] = []

        for template in template_courses:
            try:
                async with db.begin_nested():
                    course = CourseModel(
                        title=template["title"],
                        summary="",
                        template_markdown="",
                        course_json={},
                        created_by=user_id,
                        is_template=is_system_template,
                    )
                    db.add(course)
                    await db.flush()

                    if template.get("default_images"):
                        copy_default_images_for_course(
                            course_id=course.course_id,
                            template_images=template["default_images"],
                            user_id=user_id,
                            db=db,
                        )

                    summary_with_id = replace_course_id_placeholders(
                        template.get("summary") or "",
                        course.course_id,
                    )

                    template_markdown_with_id = replace_course_id_placeholders(
                        template.get("template_markdown") or "",
                        course.course_id,
                    )

                    course_json_with_id = replace_course_id_placeholders(
                        template.get("course_json") or {},
                        course.course_id,
                    )

                    questions_with_id = replace_course_id_placeholders(
                        template.get("questions") or [],
                        course.course_id,
                    )

                    quiz_with_id = replace_course_id_placeholders(
                        template.get("quiz") or "",
                        course.course_id,
                    )

                    rewritten_summary, _ = rewrite_markdown_image_urls(
                        summary_with_id,
                        course.course_id,
                    )

                    rewritten_template_markdown, _ = rewrite_markdown_image_urls(
                        template_markdown_with_id,
                        course.course_id,
                    )

                    rewritten_course_json, _ = rewrite_course_json_markdown_fields(
                        course_json_with_id,
                        course.course_id,
                    )

                    course.title = (
                        ((rewritten_course_json.get("course") or {}).get("title")
                         or template["title"])
                        .strip()
                    )
                    course.summary = rewritten_summary
                    course.template_markdown = rewritten_template_markdown
                    course.course_json = rewritten_course_json

                    if isinstance(quiz_with_id, str) and quiz_with_id.strip():
                        db.add(
                            QuizModel(
                                course_id=course.course_id,
                                content=quiz_with_id.strip(),
                            )
                        )

                    for q in questions_with_id:
                        text = (q.get("text") or "").strip()
                        answer_text = (q.get("answer_text") or "").strip()

                        if not text or not answer_text:
                            continue

                        db.add(
                            QuestionModel(
                                text=text,
                                answer_text=answer_text,
                                course_id=course.course_id,
                                created_by=user_id,
                            )
                        )

                    document_jobs.append(
                        {
                            "course_id": course.course_id,
                            "file_name": Path(
                                template.get("source_file_name") or f"default-course-{course.course_id}.md"
                            ).name,
                            "markdown_text": rewritten_template_markdown,
                        }
                    )

                    provision_report["courses_created"] += 1
                    print(f"✅ Created template course: {course.title}")

            except Exception as e:
                print(
                    f"❌ Error creating template course "
                    f"'{template.get('title', 'unknown')}': {e}"
                )
                continue

        user.template_courses_initialized = True
        await db.commit()

        for job in document_jobs:
            try:
                result = await provision_markdown_document_for_course(
                    user_id=user_id,
                    course_id=job["course_id"],
                    file_name=job["file_name"],
                    markdown_text=job["markdown_text"],
                    embedding_model_name=embedding_model_name,
                    db=db,
                )

                if result.get("ok"):
                    provision_report["documents_created"] += 1
                else:
                    provision_report["document_failures"].append(result)

            except Exception as e:
                provision_report["document_failures"].append(
                    {
                        "course_id": job["course_id"],
                        "file_name": job["file_name"],
                        "reason": str(e),
                    }
                )
                print(
                    f"⚠️ Failed to provision default document "
                    f"for course {job['course_id']}: {e}"
                )

        print(f"✅ Template provisioning report: {provision_report}")
        return provision_report

    except Exception as e:
        print(f"❌ Error in create_template_courses_for_instructor for user {user_id}: {e}")
        await db.rollback()
        return provision_report
