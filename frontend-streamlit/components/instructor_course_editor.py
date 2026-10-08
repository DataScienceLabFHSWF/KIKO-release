# frontend/components/instructor_course_editor.py
import streamlit as st, yaml
from copy import deepcopy
from i18n import translate
from .course_renderer import render_course_experience

def yaml_dump(value) -> str:
    return yaml.safe_dump(
        value if value is not None else {},
        sort_keys=False,
        allow_unicode=True,
    ).strip()

def parse_yaml_text(raw_text: str, expected_type: str, label: str):
    try:
        parsed = yaml.safe_load(raw_text)

        if parsed is None:
            parsed = {} if expected_type == "dict" else []

        if expected_type == "dict" and not isinstance(parsed, dict):
            return None, f"{label} must be a YAML mapping/object."
        if expected_type == "list" and not isinstance(parsed, list):
            return None, f"{label} must be a YAML list."

        return parsed, None
    except yaml.YAMLError as e:
        return None, f"{label} contains invalid YAML: {str(e)}"

def normalize_practice_questions(raw_questions: list, module_id: str):
    normalized = []
    errors: list[str] = []

    for idx, item in enumerate(raw_questions or [], start=1):
        if not isinstance(item, dict):
            errors.append(f"Module {module_id} practice question #{idx} must be a YAML mapping/object.")
            continue

        qid = str(item.get("id") or f"{module_id}-q{idx}").strip()
        prompt = str(item.get("prompt") or "").strip()
        reference_answer = str(item.get("reference_answer") or "").strip()
        points = item.get("points", 1)

        if not prompt:
            errors.append(f"Module {module_id} practice question #{idx} is missing 'prompt'.")
        if not reference_answer:
            errors.append(f"Module {module_id} practice question #{idx} is missing 'reference_answer'.")

        normalized.append(
            {
                "id": qid,
                "prompt": prompt,
                "reference_answer": reference_answer,
                "points": points,
            }
        )

    return normalized, errors

def build_questions_dict_from_course_json(course_json: dict) -> dict:
    qa_list: list[dict] = []

    for module in (course_json or {}).get("modules") or []:
        for item in module.get("questions") or []:
            question = str(item.get("prompt") or "").strip()
            answer = str(item.get("reference_answer") or "").strip()
            if question and answer:
                qa_list.append(
                    {
                        "question": question,
                        "answer": answer,
                    }
                )

    return {"qa_list": qa_list}

def build_summary_from_course_json(course_json: dict) -> str:
    course = (course_json or {}).get("course") or {}
    overview_md = (course_json or {}).get("overview_md") or ""
    modules = (course_json or {}).get("modules") or []

    parts = []
    title = (course.get("title") or "").strip()
    if title:
        parts.append(f"# {title}")

    if overview_md.strip():
        parts.append(overview_md.strip())

    if modules:
        module_lines = "\n".join(
            f"- {m.get('title', 'Untitled module')}" for m in modules
        )
        parts.append("## Modules\n" + module_lines)

    return "\n\n".join(p for p in parts if p).strip()

def build_markdown_from_course_json(course_json: dict) -> str:
    course_json = course_json or {}

    front_matter = {
        "schema": course_json.get("schema") or "course.v1",
        "course": course_json.get("course") or {},
        "instructors": course_json.get("instructors") or [],
        "grading": course_json.get("grading") or {},
        "resources": course_json.get("resources") or [],
    }

    course = course_json.get("course") or {}
    title = (course.get("title") or "Untitled course").strip()
    overview_md = (course_json.get("overview_md") or "").strip()
    modules = course_json.get("modules") or []
    final_quiz = course_json.get("final_quiz") or {}

    body_parts = []
    body_parts.append(f"# {title}")
    body_parts.append("## Course overview")
    body_parts.append(overview_md)
    body_parts.append("## Modules")

    for idx, module in enumerate(modules, start=1):
        module_title = module.get("title") or f"Module {idx}"
        module_id = module.get("module_id") or f"m{idx}"
        content_md = (module.get("content_md") or "").strip()
        questions_yaml = yaml_dump(module.get("questions") or [])
        quiz_yaml = yaml_dump(module.get("quiz") or {})
        further_reading_md = (module.get("further_reading_md") or "").strip()
        misconceptions_yaml = yaml_dump(module.get("misconceptions") or [])
        grade_yaml = yaml_dump(module.get("grade") or {})

        body_parts.append(f"### Module {idx}: {module_title} {{#{module_id}}}")

        body_parts.append("#### Content")
        body_parts.append(content_md)

        body_parts.append("#### Questions (practice / free-response)")
        body_parts.append("```yaml")
        body_parts.append(questions_yaml)
        body_parts.append("```")

        body_parts.append("#### Quiz (auto-graded)")
        body_parts.append("```yaml")
        body_parts.append(quiz_yaml)
        body_parts.append("```")

        body_parts.append("#### Further reading")
        body_parts.append(further_reading_md)

        body_parts.append("#### Common misconceptions")
        body_parts.append("```yaml")
        body_parts.append(misconceptions_yaml)
        body_parts.append("```")

        body_parts.append("#### Grade")
        body_parts.append("```yaml")
        body_parts.append(grade_yaml)
        body_parts.append("```")

    body_parts.append("## Overall Quiz")
    body_parts.append("```yaml")
    body_parts.append(yaml_dump(final_quiz))
    body_parts.append("```")

    front_matter_text = yaml.safe_dump(
        front_matter,
        sort_keys=False,
        allow_unicode=True,
    ).strip()

    body_text = "\n\n".join(part for part in body_parts if part is not None).strip()
    return f"---\n{front_matter_text}\n---\n\n{body_text}\n"

def build_save_payload_from_course_json(course_json: dict, title_override: str | None = None) -> dict:
    course_json_to_save = deepcopy(course_json or {})
    if title_override and title_override.strip():
        course_json_to_save.setdefault("course", {})
        course_json_to_save["course"]["title"] = title_override.strip()

    generated_summary = build_summary_from_course_json(course_json_to_save)
    generated_template_markdown = build_markdown_from_course_json(course_json_to_save)
    generated_final_quiz_yaml = yaml_dump(course_json_to_save.get("final_quiz") or {})
    synced_questions_dict = build_questions_dict_from_course_json(course_json_to_save)

    return {
        "title": ((course_json_to_save.get("course") or {}).get("title") or "").strip(),
        "summary": generated_summary,
        "questions": [
            {"text": q.get("question", ""), "answer_text": q.get("answer", "")}
            for q in synced_questions_dict.get("qa_list", [])
        ],
        "template_markdown": generated_template_markdown,
        "course_json": course_json_to_save,
        "quiz": generated_final_quiz_yaml,
        "questions_dict": synced_questions_dict,
    }

def render_instructor_course_editor(course_json: dict, state_prefix: str = "course_editor", request_headers: dict | None = None):
    edited = deepcopy(course_json or {})
    validation_errors: list[str] = []

    editor_version_key = f"{state_prefix}_editor_version"
    if editor_version_key not in st.session_state:
        st.session_state[editor_version_key] = 0
    editor_version = st.session_state[editor_version_key]

    course = edited.setdefault("course", {})
    edited.setdefault("instructors", [])
    edited.setdefault("grading", {})
    edited.setdefault("resources", [])
    edited.setdefault("modules", [])
    edited.setdefault("final_quiz", {})

    tabs = st.tabs(
        [
            translate("instructor_course_editor.tabs.learner_preview"),
            translate("instructor_course_editor.tabs.course"),
            translate("instructor_course_editor.tabs.modules"),
            translate("instructor_course_editor.tabs.final_quiz"),
            translate("instructor_course_editor.tabs.resources_grading"),
            translate("instructor_course_editor.tabs.raw_json")
        ]
    )

    with tabs[1]:
        c1, c2, c3 = st.columns(3)
        course["title"] = c1.text_input(
            translate("instructor_course_editor.course_title"),
            value=course.get("title", ""),
            key=f"{state_prefix}_title_{editor_version}",
        )
        course["provider"] = c2.text_input(
            translate("instructor_course_editor.provider"),
            value=course.get("provider", "") or "",
            key=f"{state_prefix}_provider_{editor_version}",
        )
        course["language"] = c3.text_input(
            translate("instructor_course_editor.language"),
            value=course.get("language", "") or "",
            key=f"{state_prefix}_language_{editor_version}",
        )

        c4, c5, c6 = st.columns(3)
        course["level"] = c4.text_input(
            translate("instructor_course_editor.level"),
            value=course.get("level", "") or "",
            key=f"{state_prefix}_level_{editor_version}",
        )
        course["id"] = c5.text_input(
            translate("instructor_course_editor.course_id"),
            value=course.get("id", "") or "",
            key=f"{state_prefix}_course_id_{editor_version}",
        )
        course["estimated_minutes"] = c6.number_input(
            translate("instructor_course_editor.estimated_modules"),
            value=int(course.get("estimated_minutes") or 0),
            min_value=0,
            step=5,
            key=f"{state_prefix}_estimated_minutes_{editor_version}",
        )

        tags_text = st.text_input(
            translate("instructor_course_editor.tags_comma"),
            value=", ".join(course.get("tags") or []),
            key=f"{state_prefix}_tags_{editor_version}",
        )
        course["tags"] = [t.strip() for t in tags_text.split(",") if t.strip()]

        prereq_text = st.text_area(
            translate("instructor_course_editor.prerequisites"),
            value="\n".join(course.get("prerequisites") or []),
            height=120,
            key=f"{state_prefix}_prereq_{editor_version}",
        )
        course["prerequisites"] = [p.strip() for p in prereq_text.splitlines() if p.strip()]

        edited["overview_md"] = st.text_area(
            translate("instructor_course_editor.course_overview"),
            value=edited.get("overview_md", "") or "",
            height=260,
            key=f"{state_prefix}_overview_{editor_version}",
        )

    with tabs[2]:
        modules = edited.get("modules") or []

        if not modules:
            st.info(translate("instructor_course_editor.info.no_modules"))
        else:
            module_index = st.selectbox(
                translate("instructor_course_editor.select_module"),
                options=list(range(len(modules))),
                format_func=lambda i: f"Module {i+1}: {modules[i].get('title', 'Untitled')}",
                key=f"{state_prefix}_module_select_{editor_version}",
            )

            module = modules[module_index]
            module_id = module.get("module_id", f"m{module_index+1}")

            module["title"] = st.text_input(
                translate("instructor_course_editor.module_title"),
                value=module.get("title", "") or "",
                key=f"{state_prefix}_module_title_{editor_version}_{module_id}",
            )

            module["content_md"] = st.text_area(
                translate("instructor_course_editor.content_md"),
                value=module.get("content_md", "") or "",
                height=300,
                key=f"{state_prefix}_module_content_{editor_version}_{module_id}",
            )

            practice_yaml_text = st.text_area(
                translate("instructor_course_editor.practice_que_yaml"),
                value=yaml_dump(module.get("questions") or []),
                height=320,
                key=f"{state_prefix}_module_questions_{editor_version}_{module_id}",
            )
            parsed_questions, err = parse_yaml_text(
                practice_yaml_text,
                expected_type="list",
                label=f"Module {module_id} practice questions",
            )
            if err:
                validation_errors.append(err)
                st.error(err)
            else:
                normalized_questions, q_errors = normalize_practice_questions(parsed_questions, module_id=module_id)
                if q_errors:
                    validation_errors.extend(q_errors)
                    for msg in q_errors:
                        st.error(msg)
                module["questions"] = normalized_questions

            quiz_yaml_text = st.text_area(
                translate("instructor_course_editor.quiz_yaml"),
                value=yaml_dump(module.get("quiz") or {}),
                height=340,
                key=f"{state_prefix}_module_quiz_{editor_version}_{module_id}",
            )
            parsed_quiz, err = parse_yaml_text(
                quiz_yaml_text,
                expected_type="dict",
                label=f"Module {module_id} quiz",
            )
            if err:
                validation_errors.append(err)
                st.error(err)
            else:
                module["quiz"] = parsed_quiz

            module["further_reading_md"] = st.text_area(
                translate("instructor_course_editor.further_reading"),
                value=module.get("further_reading_md", "") or "",
                height=180,
                key=f"{state_prefix}_module_further_{editor_version}_{module_id}",
            )

            misconceptions_yaml_text = st.text_area(
                translate("instructor_course_editor.common_misconceptions"),
                value=yaml_dump(module.get("misconceptions") or []),
                height=220,
                key=f"{state_prefix}_module_misconceptions_{editor_version}_{module_id}",
            )
            parsed_misconceptions, err = parse_yaml_text(
                misconceptions_yaml_text,
                expected_type="list",
                label=f"Module {module_id} misconceptions",
            )
            if err:
                validation_errors.append(err)
                st.error(err)
            else:
                module["misconceptions"] = parsed_misconceptions

            grade_yaml_text = st.text_area(
                translate("instructor_course_editor.grade_yaml"),
                value=yaml_dump(module.get("grade") or {}),
                height=200,
                key=f"{state_prefix}_module_grade_{editor_version}_{module_id}",
            )
            parsed_grade, err = parse_yaml_text(
                grade_yaml_text,
                expected_type="dict",
                label=f"Module {module_id} grade",
            )
            if err:
                validation_errors.append(err)
                st.error(err)
            else:
                module["grade"] = parsed_grade

    with tabs[3]:
        final_quiz_yaml_text = st.text_area(
            translate("instructor_course_editor.final_quiz_yaml"),
            value=yaml_dump(edited.get("final_quiz") or {}),
            height=420,
            key=f"{state_prefix}_final_quiz_{editor_version}",
        )
        parsed_final_quiz, err = parse_yaml_text(
            final_quiz_yaml_text,
            expected_type="dict",
            label="Final quiz",
        )
        if err:
            validation_errors.append(err)
            st.error(err)
        else:
            edited["final_quiz"] = parsed_final_quiz

    with tabs[4]:
        instructors_yaml_text = st.text_area(
            translate("instructor_course_editor.instructors_yaml"),
            value=yaml_dump(edited.get("instructors") or []),
            height=180,
            key=f"{state_prefix}_instructors_{editor_version}",
        )
        parsed_instructors, err = parse_yaml_text(
            instructors_yaml_text,
            expected_type="list",
            label="Instructors",
        )
        if err:
            validation_errors.append(err)
            st.error(err)
        else:
            edited["instructors"] = parsed_instructors

        resources_yaml_text = st.text_area(
            translate("instructor_course_editor.resources_yaml"),
            value=yaml_dump(edited.get("resources") or []),
            height=220,
            key=f"{state_prefix}_resources_{editor_version}",
        )
        parsed_resources, err = parse_yaml_text(
            resources_yaml_text,
            expected_type="list",
            label="Resources",
        )
        if err:
            validation_errors.append(err)
            st.error(err)
        else:
            edited["resources"] = parsed_resources

        grading_yaml_text = st.text_area(
            translate("instructor_course_editor.grading_yaml"),
            value=yaml_dump(edited.get("grading") or {}),
            height=260,
            key=f"{state_prefix}_grading_{editor_version}",
        )
        parsed_grading, err = parse_yaml_text(
            grading_yaml_text,
            expected_type="dict",
            label="Grading",
        )
        if err:
            validation_errors.append(err)
            st.error(err)
        else:
            edited["grading"] = parsed_grading

    with tabs[5]:
        st.json(edited)

    with tabs[0]:
        render_course_experience(
            edited,
            mode="instructor_preview",
            state_prefix=f"{state_prefix}_preview",
            show_sidebar_nav=True,
            request_headers=request_headers,
        )

    if validation_errors:
        st.warning(translate("instructor_course_editor.warning.yaml_validation"))

    synced_questions_dict = build_questions_dict_from_course_json(edited)
    return edited, validation_errors, synced_questions_dict
