import re, yaml
from typing import Any, Optional

class CourseMarkdownStructureError(ValueError):
    pass

COURSE_SCHEMA = "course.v1"

REQUIRED_COURSE_H2 = {
    "course overview": {
        "display": "Course overview",
        "aliases": ("course overview", "kursübersicht"),
    },
    "modules": {
        "display": "Modules",
        "aliases": ("modules", "module"),
    },
    "overall quiz": {
        "display": "Overall Quiz",
        "aliases": ("overall quiz", "gesamtquiz"),
    },
}

REQUIRED_MODULE_H4 = {
    "content": {
        "display": "Content",
        "aliases": ("content", "inhalt"),
    },
    "questions (practice / free-response)": {
        "display": "Questions (practice / free-response)",
        "aliases": ("questions (practice / free-response)", "fragen (übung / freitext)"),
    },
    "quiz (auto-graded)": {
        "display": "Quiz (auto-graded)",
        "aliases": ("quiz (auto-graded)", "quiz (automatisch bewertet)"),
    },
    "further reading": {
        "display": "Further reading",
        "aliases": ("further reading", "weiterführende inhalte"),
    },
    "common misconceptions": {
        "display": "Common misconceptions",
        "aliases": ("common misconceptions", "häufige missverständnisse"),
    },
    "grade": {
        "display": "Grade",
        "aliases": ("grade", "bewertung"),
    },
}


def resolve_required_sections(
    section_map: dict[str, Any],
    required_definitions: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], list[str]]:
    resolved: dict[str, Any] = {}
    missing: list[str] = []

    for canonical_key, definition in required_definitions.items():
        aliases = definition.get("aliases") or ()
        matched_value = None
        for alias in aliases:
            if alias in section_map:
                matched_value = section_map[alias]
                break

        if matched_value is None:
            missing.append(str(definition.get("display") or canonical_key))
        else:
            resolved[canonical_key] = matched_value

    return resolved, missing

def serialize_metadata(obj: Any) -> Any:
    """
    Makes YAML-loaded metadata JSON-serializable and predictable.
    """
    if isinstance(obj, dict):
        return {str(k): serialize_metadata(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize_metadata(v) for v in obj]
    return obj

def normalize_heading(text: str) -> str:
    """
    Lowercases and strips anchor ids like {#m1}.
    """
    text = re.sub(r"\s*\{#.*?\}\s*$", "", text.strip())
    text = re.sub(r"\s+", " ", text)
    return text.lower()

def extract_anchor_id(text: str) -> Optional[str]:
    match = re.search(r"\{#([^}]+)\}\s*$", text.strip())
    return match.group(1).strip() if match else None

def split_markdown_sections_by_level(text: str, level: int) -> list[dict[str, str]]:
    """
    Splits markdown by an exact heading level, e.g. ## or ### or ####.
    """
    heading = "#" * level
    pattern = re.compile(rf"(?m)^(?P<raw>{re.escape(heading)}\s+(?P<title>.+?)\s*)$")
    matches = list(pattern.finditer(text))

    sections: list[dict[str, str]] = []
    for idx, match in enumerate(matches):
        body_start = match.end()
        body_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        title = match.group("title").strip()

        sections.append(
            {
                "title": title,
                "normalized_title": normalize_heading(title),
                "body": text[body_start:body_end].strip(),
            }
        )
    return sections

def extract_single_yaml_fence(section_text: str, section_name: str) -> Any:
    match = re.search(r"```yaml\s*(.*?)```", section_text, re.DOTALL | re.IGNORECASE)
    if not match:
        raise CourseMarkdownStructureError(
            f"❌ Section '{section_name}' must contain a ```yaml ...``` fenced block"
        )

    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        raise CourseMarkdownStructureError(
            f"❌ Invalid YAML in section '{section_name}': {exc}"
        ) from exc

def parse_module_header(header: str) -> tuple[str, str]:
    """
    Example:
      Module 1: 1_Einleitung und Lernziele {#m1}
    """
    pattern = re.compile(
        r"^(?:Module|Modul)\s+\d+\s*:\s*(?P<title>.*?)\s*(?:\{#(?P<anchor>[^}]+)\})?\s*$",
        re.IGNORECASE,
    )
    match = pattern.match(header.strip())
    if not match:
        raise CourseMarkdownStructureError(f"❌Invalid module header: '{header}'")

    title = (match.group("title") or "").strip()
    anchor = (match.group("anchor") or "").strip()

    if not title:
        raise CourseMarkdownStructureError(f"❌ Module title missing in header: '{header}'")
    if not anchor:
        raise CourseMarkdownStructureError(
            f"❌ Module anchor id missing in header: '{header}'. Expected '{{#mX}}'."
        )

    return title, anchor

def validate_practice_questions(raw_questions: Any, module_title: str) -> list[dict[str, Any]]:
    if not isinstance(raw_questions, list) or not raw_questions:
        raise CourseMarkdownStructureError(
            f"❌ Module '{module_title}' questions must be a non-empty YAML list"
        )

    validated: list[dict[str, Any]] = []
    for idx, item in enumerate(raw_questions, start=1):
        if not isinstance(item, dict):
            raise CourseMarkdownStructureError(
                f"❌ Module '{module_title}' question #{idx} must be a YAML mapping"
            )

        qid = str(item.get("id") or "").strip()
        prompt = str(item.get("prompt") or "").strip()
        reference_answer = str(item.get("reference_answer") or "").strip()
        points = item.get("points", 1)

        if not qid or not prompt or not reference_answer:
            raise CourseMarkdownStructureError(
                f"❌ Module '{module_title}' question #{idx} must include id, prompt, and reference_answer"
            )

        validated.append(
            {
                "id": qid,
                "prompt": prompt,
                "reference_answer": reference_answer,
                "points": points,
            }
        )
    return validated

def validate_quiz(raw_quiz: Any, section_name: str) -> dict[str, Any]:
    if not isinstance(raw_quiz, dict):
        raise CourseMarkdownStructureError(f"{section_name} must be a YAML mapping")

    meta = raw_quiz.get("meta") or {}
    items = raw_quiz.get("items") or []

    if not isinstance(meta, dict):
        raise CourseMarkdownStructureError(f"{section_name}.meta must be a mapping")
    if not isinstance(items, list) or not items:
        raise CourseMarkdownStructureError(f"{section_name}.items must be a non-empty list")

    quiz_id = str(meta.get("id") or "").strip()
    quiz_title = str(meta.get("title") or "").strip()
    if not quiz_id or not quiz_title:
        raise CourseMarkdownStructureError(f"{section_name}.meta must include id and title")

    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise CourseMarkdownStructureError(f"{section_name} item #{idx} must be a mapping")
        item_id = str(item.get("id") or "").strip()
        item_type = str(item.get("type") or "").strip()
        prompt = str(item.get("prompt") or "").strip()
        if not item_id or not item_type or not prompt:
            raise CourseMarkdownStructureError(
                f"❌ {section_name} item #{idx} must include id, type, and prompt"
            )

    return raw_quiz

def validate_misconceptions(raw_data: Any, module_title: str) -> list[dict[str, str]]:
    if not isinstance(raw_data, list):
        raise CourseMarkdownStructureError(
            f"❌ Module '{module_title}' misconceptions must be a YAML list"
        )

    validated: list[dict[str, str]] = []
    for idx, item in enumerate(raw_data, start=1):
        if not isinstance(item, dict):
            raise CourseMarkdownStructureError(
                f"❌ Module '{module_title}' misconception #{idx} must be a YAML mapping"
            )
        validated.append(
            {
                "misconception": str(item.get("misconception") or "").strip(),
                "correction": str(item.get("correction") or "").strip(),
            }
        )
    return validated

def validate_grade_block(raw_data: Any, module_title: str) -> dict[str, Any]:
    if not isinstance(raw_data, dict):
        raise CourseMarkdownStructureError(f"❌ Module '{module_title}' grade block must be a YAML mapping")
    return raw_data

def parse_course_markdown(text: str) -> dict[str, Any]:
    front_matter_pattern = re.compile(r"^\ufeff?---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    front_match = front_matter_pattern.match(text)

    if not front_match:
        raise CourseMarkdownStructureError(
            "❌ Markdown file must start with a YAML front matter block delimited by ---"
        )

    try:
        metadata_raw = yaml.safe_load(front_match.group(1)) or {}
    except yaml.YAMLError as exc:
        raise CourseMarkdownStructureError(f"❌ Invalid YAML front matter: {exc}") from exc

    if not isinstance(metadata_raw, dict):
        raise CourseMarkdownStructureError("❌ Front matter must be a YAML mapping")

    metadata = serialize_metadata(metadata_raw)

    schema_name = metadata.get("schema")
    if schema_name != COURSE_SCHEMA:
        raise CourseMarkdownStructureError(
            f"❌ Unsupported schema '{schema_name}'. Expected '{COURSE_SCHEMA}'."
        )

    course_meta = metadata.get("course") or {}
    if not isinstance(course_meta, dict):
        raise CourseMarkdownStructureError("❌ Front matter must include a 'course' mapping")

    source_id = str(course_meta.get("id") or "").strip()
    course_title = str(course_meta.get("title") or "").strip()
    if not source_id:
        raise CourseMarkdownStructureError("❌ Front matter must include course.id")
    if not course_title:
        raise CourseMarkdownStructureError("❌ Front matter must include course.title")

    body = text[front_match.end():].strip()
    if not body:
        raise CourseMarkdownStructureError("❌ Markdown body is empty")

    h2_sections = split_markdown_sections_by_level(body, level=2)
    h2_map = {sec["normalized_title"]: sec for sec in h2_sections}
    resolved_h2, missing_h2 = resolve_required_sections(h2_map, REQUIRED_COURSE_H2)
    if missing_h2:
        raise CourseMarkdownStructureError(
            f"❌ Markdown document missing required course sections: {', '.join(missing_h2)}"
        )

    overview_md = resolved_h2["course overview"]["body"].strip()
    modules_block = resolved_h2["modules"]["body"].strip()
    overall_quiz_block = resolved_h2["overall quiz"]["body"].strip()

    if not overview_md:
        raise CourseMarkdownStructureError("❌ Course overview section must not be empty")

    module_sections = split_markdown_sections_by_level(modules_block, level=3)
    if not module_sections:
        raise CourseMarkdownStructureError("❌ Modules section must contain at least one module")

    modules: list[dict[str, Any]] = []
    flat_qa_list: list[dict[str, str]] = []
    embedding_units: list[dict[str, Any]] = []

    for module_section in module_sections:
        module_title, module_id = parse_module_header(module_section["title"])
        h4_sections = split_markdown_sections_by_level(module_section["body"], level=4)
        h4_map = {sec["normalized_title"]: sec["body"] for sec in h4_sections}
        resolved_h4, missing_h4 = resolve_required_sections(h4_map, REQUIRED_MODULE_H4)
        if missing_h4:
            raise CourseMarkdownStructureError(
                f"❌ Module '{module_title}' is missing required subsections: {', '.join(missing_h4)}"
            )

        content_md = resolved_h4["content"].strip()
        further_reading_md = resolved_h4["further reading"].strip()

        raw_questions = extract_single_yaml_fence(
            resolved_h4["questions (practice / free-response)"],
            f"Module '{module_title}' questions",
        )
        raw_quiz = extract_single_yaml_fence(
            resolved_h4["quiz (auto-graded)"],
            f"Module '{module_title}' quiz",
        )
        raw_misconceptions = extract_single_yaml_fence(
            resolved_h4["common misconceptions"],
            f"Module '{module_title}' common misconceptions",
        )
        raw_grade = extract_single_yaml_fence(
            resolved_h4["grade"],
            f"Module '{module_title}' grade",
        )

        practice_questions = validate_practice_questions(raw_questions, module_title)
        quiz = validate_quiz(raw_quiz, f"Module '{module_title}' quiz")
        misconceptions = validate_misconceptions(raw_misconceptions, module_title)
        grade = validate_grade_block(raw_grade, module_title)

        for q in practice_questions:
            flat_qa_list.append(
                {
                    "question": q["prompt"],
                    "answer": q["reference_answer"],
                }
            )

        module_payload = {
            "module_id": module_id,
            "title": module_title,
            "content_md": content_md,
            "questions": practice_questions,
            "quiz": quiz,
            "further_reading_md": further_reading_md,
            "misconceptions": misconceptions,
            "grade": grade,
        }
        modules.append(module_payload)

        embedding_text_parts = [
            f"# {module_title}",
            content_md,
        ]
        if further_reading_md:
            embedding_text_parts.append("## Further reading")
            embedding_text_parts.append(further_reading_md)

        embedding_units.append(
            {
                "module_id": module_id,
                "module_title": module_title,
                "text": "\n\n".join(p for p in embedding_text_parts if p).strip(),
            }
        )

    overall_quiz = validate_quiz(
        extract_single_yaml_fence(overall_quiz_block, "Overall Quiz"),
        "Overall Quiz",
    )

    summary_parts = [
        f"# {course_title}",
        overview_md,
        "## Modules",
        "\n".join(f"- {module['title']}" for module in modules),
    ]
    summary_text = "\n\n".join(part for part in summary_parts if part).strip()

    questions_dict = {"qa_list": flat_qa_list}

    course_json = {
        "schema": metadata.get("schema"),
        "course": metadata.get("course") or {},
        "instructors": metadata.get("instructors") or [],
        "grading": metadata.get("grading") or {},
        "resources": metadata.get("resources") or [],
        "overview_md": overview_md,
        "modules": modules,
        "final_quiz": overall_quiz,
    }

    return {
        "metadata": metadata,
        "source_id": source_id,
        "summary": summary_text,
        "questions_dict": questions_dict,
        "quiz_dict": overall_quiz,
        "quiz_yaml_str": yaml.safe_dump(
            overall_quiz,
            sort_keys=False,
            allow_unicode=True,
        ).strip(),
        "course_json": course_json,
        "embedding_units": embedding_units,
        "template_markdown": text,
    }
