# frontend/components/course_renderer.py
import requests, streamlit as st
from typing import Any, Dict, Literal
from utils import render_markdown_with_images, grade_label, grade_status_variant
from i18n import translate

RenderMode = Literal["instructor_preview", "learner"]

def _state_key(prefix: str, name: str) -> str:
    return f"{prefix}_{name}"

def _safe_list(value: Any) -> list:
    return value if isinstance(value, list) else []

def _safe_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}

def _default_course_completion(
    is_enrolled: bool = False
) -> dict:
    return {
        "status": "in_progress" if is_enrolled else "not_enrolled",
        "eligible_for_final_quiz": False,
        "completed": False,
        "weighted_percent": None,
        "german_grade": None,
    }

def _default_progress_snapshot(
    is_enrolled: bool = False
) -> dict:
    return {
        "current_nav": "overview",
        "current_module_id": None,
        "completion_percent": 0.0,
        "module_status": {},
        "final_status": {},
        "practice_answers": {},
        "course_completion": _default_course_completion(is_enrolled=is_enrolled),
    }

def _merge_progress_snapshot(
    base: dict | None, 
    incoming: dict | None,
    is_enrolled: bool = False,
) -> dict:
    
    base = _safe_dict(base)
    incoming = _safe_dict(incoming)

    merged = _default_progress_snapshot(is_enrolled=is_enrolled)

    merged["current_nav"] = incoming.get(
        "current_nav", 
        base.get("current_nav", merged["current_nav"])
    )

    merged["current_module_id"] = incoming.get(
        "current_module_id", 
        base.get("current_module_id")
    )
    try:
        merged["completion_percent"] = float(
            incoming.get(
                "completion_percent", 
                base.get("completion_percent", 0.0)
            )
        )
    except Exception:
        merged["completion_percent"] = 0.0
    
    merged["module_status"] = {
        **{str(k): _safe_dict(v) for k, v in _safe_dict(base.get("module_status")).items()},
        **{str(k): _safe_dict(v) for k, v in _safe_dict(incoming.get("module_status")).items()},
    }

    merged["final_status"] = {
        **_safe_dict(base.get("final_status")),
        **_safe_dict(incoming.get("final_status")),
    }

    merged["practice_answers"] = {
        **_safe_dict(base.get("practice_answers")),
        **_safe_dict(incoming.get("practice_answers")),
    }

    merged["course_completion"] = {
        **_default_course_completion(is_enrolled=is_enrolled),
        **_safe_dict(base.get("course_completion")),
        **_safe_dict(incoming.get("course_completion")),
    }
    
    return merged

def _normalize_progress_snapshot(
    snapshot: dict | None,
    is_enrolled: bool = False,
) -> dict:
    return _merge_progress_snapshot(
        _default_progress_snapshot(is_enrolled=is_enrolled),
        snapshot,
        is_enrolled=is_enrolled,
    )

def _store_progress_snapshot(
    prefix: str, 
    snapshot: dict | None,
    is_enrolled: bool = False,
):
    key = _state_key(prefix, "progress_snapshot")
    
    merged = _merge_progress_snapshot(
        st.session_state.get(key),
        snapshot,
        is_enrolled=is_enrolled,
    )
    st.session_state[key] = merged
    return merged

def _format_duration(minutes: Any) -> str:
    try:
        minutes = int(minutes)
    except Exception:
        return "—"

    hours = minutes // 60
    rem = minutes % 60
    if hours and rem:
        return f"{hours}h {rem}m"
    if hours:
        return f"{hours}h"
    return f"{rem} min"

def _render_markdown_block(md_text: str, request_headers: dict | None = None):
    if not md_text:
        st.info(translate("course_render.no_contents"))
        return
    render_markdown_with_images(md_text, headers=request_headers)

def inject_course_styles():
    st.markdown(
        """
        <style>
        .course-shell {
            background: linear-gradient(180deg, #f7f9fc 0%, #ffffff 100%);
            border-radius: 18px;
            padding: 0.25rem 0.25rem 1rem 0.25rem;
        }
        .course-hero {
            background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 45%, #2563eb 100%);
            color: white;
            border-radius: 22px;
            padding: 1.4rem 1.6rem;
            margin-bottom: 1rem;
            box-shadow: 0 10px 24px rgba(15, 23, 42, 0.16);
        }
        .course-hero h1 {
            margin: 0 0 0.3rem 0;
            font-size: 2rem;
            line-height: 1.15;
        }
        .course-hero p {
            margin: 0.15rem 0 0 0;
            opacity: 0.94;
        }
        .metric-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 0.9rem 1rem;
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.04);
        }
        .metric-card .label {
            color: #64748b;
            font-size: 0.86rem;
            margin-bottom: 0.2rem;
        }
        .metric-card .value {
            color: #0f172a;
            font-size: 1.05rem;
            font-weight: 700;
        }
        .section-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 1rem 1rem 0.7rem 1rem;
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.04);
            margin-bottom: 1rem;
        }
        .section-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: #0f172a;
            margin-bottom: 0.55rem;
        }
        .curriculum-card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 1rem;
            box-shadow: 0 6px 16px rgba(15, 23, 42, 0.04);
        }
        .tag-chip {
            display: inline-block;
            padding: 0.25rem 0.55rem;
            margin: 0.1rem 0.35rem 0.15rem 0;
            border-radius: 999px;
            background: #eff6ff;
            color: #1d4ed8;
            border: 1px solid #bfdbfe;
            font-size: 0.82rem;
            font-weight: 600;
        }
        .resource-pill {
            display: inline-block;
            padding: 0.18rem 0.5rem;
            border-radius: 999px;
            background: #f8fafc;
            color: #475569;
            border: 1px solid #e2e8f0;
            font-size: 0.78rem;
            margin-bottom: 0.4rem;
        }
        .small-muted {
            color: #64748b;
            font-size: 0.86rem;
        }
        .overview-box {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            padding: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def _extract_overview_learnings(overview_md: str) -> list[str]:
    """
    Very light parser:
    collects bullet lines after 'Learning outcomes' heading if present.
    """
    if not isinstance(overview_md, str) or not overview_md.strip():
        return []

    lines = overview_md.splitlines()
    results: list[str] = []
    capture = False
    for line in lines:
        stripped = line.strip()
        lowered = stripped.lower()
        if lowered.startswith("### learning outcomes") or lowered.startswith("### lernziele"):
            capture = True
            continue
        if capture:
            if stripped.startswith("### "):
                break
            if stripped.startswith("- "):
                results.append(stripped[2:].strip())
    return results

def _initialize_progress_state(
    prefix: str, 
    incoming_snapshot: dict | None,
    is_enrolled: bool,
):
    progress_key = _state_key(prefix, "progress_snapshot")
    
    if not is_enrolled:
        empty_snapshot = _default_progress_snapshot(is_enrolled=False)
        empty_snapshot["course_completion"]["status"] = "not_enrolled"
        st.session_state[progress_key] = empty_snapshot
        return empty_snapshot
    
    current_snapshot = _safe_dict(st.session_state.get(progress_key))

    if not current_snapshot:
        return _store_progress_snapshot(prefix, incoming_snapshot, is_enrolled)

    if incoming_snapshot:
        return _store_progress_snapshot(
            prefix,
            _merge_progress_snapshot(current_snapshot, incoming_snapshot, is_enrolled),
        )

    st.session_state[progress_key] = _normalize_progress_snapshot(current_snapshot, is_enrolled)
    return st.session_state[progress_key]

def _save_progress(
    api_base: str,
    request_headers: dict,
    course_id: int,
    current_nav: str | None,
    current_module_id: str | None,
    practice_answers: dict | None,
):
    payload = {
        "current_nav": current_nav,
        "current_module_id": current_module_id,
        "practice_answers": practice_answers or {},
    }

    r = requests.put(
        f"{api_base}/api/learner/courses/{course_id}/progress",
        json=payload,
        headers=request_headers
    )

    if not r.ok:
        try:
            detail = r.json().get("detail")
        except Exception:
            detail = r.text
        raise RuntimeError(translate("course_render.errors.saveProgressFailed", details=detail))
    return r.json().get("progress_snapshot") or {}

def _submit_quiz_attempt(
    api_base: str,
    auth_headers: dict,
    course_id: int,
    assessment_type: str,
    module_id: str,
    assessment_id: str,
    answers: list[dict],
    reasoning_model: str | None,
):
    payload = {
        "assessment_id": assessment_id,
        "reasoning_model_name": reasoning_model,
        "answers": answers,
    }

    if assessment_type == "module_quiz":
        if not module_id:
            raise RuntimeError("module_id is required for module quiz submission")
        
        url = f"{api_base}/api/learner/courses/{course_id}/module-quizzes/{module_id}/submit"
    elif assessment_type == "final_quiz":
        url = f"{api_base}/api/learner/courses/{course_id}/final-quiz/submit"
    else:
        raise RuntimeError(f"Unsupported assessment_type: {assessment_type}")
    
    r = requests.post(
        url,
        json=payload,
        headers=auth_headers,
    )
    
    if not r.ok:
        try:
            detail = r.json().get("detail")
        except Exception:
            detail = r.text
        raise RuntimeError(translate("course_render.errors.submitQuizFailed", details=detail))

    return r.json()

def _evaluate_practice_answer(
    api_base: str,
    auth_headers: dict,
    question: str,
    reference_answer: str,
    user_answer: str,
    reasoning_model: str | None
):
    payload = {
        "question": question,
        "reference_answer": reference_answer,
        "user_answer": user_answer,
        "reasoning_model_name": reasoning_model
    }
    r = requests.post(
        f"{api_base}/api/course/answer_grading",
        json=payload,
        headers=auth_headers
    )

    if r.status_code == 200:
        return r.json()
    
    try:
        detail = r.json().get("detail")
    except Exception:
        detail = r.text

    raise RuntimeError(
        translate("course_render.errors.evaluateAnswerFailed", details=detail or r.status_code)
    )

def _compute_progress(
    course_json: dict, 
    progress_snapshot: dict | None
) -> tuple[int, int, float]:
    
    progress_snapshot = _normalize_progress_snapshot(progress_snapshot)
    
    modules = _safe_list(course_json.get("modules"))
    final_quiz = _safe_dict(course_json.get("final_quiz"))

    total_steps = len(modules) + (1 if final_quiz.get("items") else 0)
    if total_steps == 0:
        return 0, 0, 0.0

    raw_module_status = _safe_dict(progress_snapshot.get("module_status"))
    module_status = {str(k): _safe_dict(v) for k, v in raw_module_status.items()}

    completed_modules = sum(
        1
        for m in modules
        if module_status.get(str(m.get("module_id")), {}).get("quiz_passed")
    )

    final_status = _safe_dict(progress_snapshot.get("final_status"))
    completed_final = 1 if final_status.get("passed") else 0

    completed = completed_modules + completed_final
    return completed, total_steps, completed / total_steps

def _can_attempt_final_quiz(
    course_json: dict, 
    progress_snapshot: dict
) -> tuple[bool, str | None]:
    
    progress_snapshot = _normalize_progress_snapshot(progress_snapshot)
    
    grading = _safe_dict(course_json.get("grading"))
    completion = _safe_dict(_safe_dict(grading.get("policy")).get("completion"))
    required_modules = _safe_list(completion.get("required_modules"))

    if not required_modules:
        required_modules = [
            str(m.get("module_id"))
            for m in _safe_list(course_json.get("modules"))
            if m.get("module_id") is not None
        ]
    
    raw_module_status = _safe_dict(progress_snapshot.get("module_status"))
    module_status = {str(k): _safe_dict(v) for k, v in raw_module_status.items()}

    missing = []
    for module_id in required_modules:
        if not module_status.get(str(module_id), {}).get("quiz_passed"):
            missing.append(str(module_id))

    if missing:
        return False, translate(
            "course_render.warnings.missingModulesFinalQuiz",
            missing=", ".join(missing),
        )

    return True, None

def _render_hero(course_json: dict, mode: RenderMode, progress_snapshot: dict):
    course = _safe_dict(course_json.get("course"))
    modules = _safe_list(course_json.get("modules"))
    resources = _safe_list(course_json.get("resources"))
    completed_steps, total_steps, progress = _compute_progress(course_json, progress_snapshot)

    title = course.get("title", "Course")
    provider = course.get("provider", "")
    level = course.get("level", "")
    language = course.get("language", "")
    estimated_minutes = course.get("estimated_minutes")
    duration = _format_duration(estimated_minutes)

    st.markdown('<div class="course-shell">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="course-hero">
            <div class="small-muted" style="color:#dbeafe;">{provider or translate("course_render.warnings.noProviderName")}</div>
            <h1>{title}</h1>
            <p>{level or translate("course_render.warnings.noLevelSet")} · {language or translate("course_render.warnings.noLanguageSet")} · {duration}</p>
            <p style="margin-top:0.55rem;">{len(modules)} modules · {len(resources)} resources · {completed_steps}/{total_steps or 0} passed assessments</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f'<div class="metric-card"><div class="label">{translate("course_render.difficulty")}</div><div class="value">{level or "—"}</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="metric-card"><div class="label">{translate("course_render.duration")}</div><div class="value">{duration}</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="metric-card"><div class="label">{translate("course_render.modules")}</div><div class="value">{len(modules)}</div></div>',
            unsafe_allow_html=True,
        )
    with m4:
        label = translate("course_render.previewCompleteness") if mode == "instructor_preview" else translate("course_render.assessmentProgress")
        st.markdown(
            f'<div class="metric-card"><div class="label">{label}</div><div class="value">{progress * 100:.0f}%</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

def _render_sidebar(course_json: dict, prefix: str) -> tuple[list[str], list[tuple[str, str]]]:
    modules = _safe_list(course_json.get("modules"))
    final_quiz = _safe_dict(course_json.get("final_quiz"))

    nav_items = [
        ("overview", translate("course_render.nav_bar.course_overview")), 
        ("about", translate("course_render.nav_bar.course_info"))
    ]
    
    for idx, module in enumerate(modules):
        nav_items.append((f"module_{idx}", f"📘 Module {idx + 1}: {module.get('title', 'Untitled')}"))
    
    if final_quiz.get("items"):
        nav_items.append(("final_quiz", translate("course_render.nav_bar.course_final_quiz")))
    
    nav_items.extend([
        ("grades", translate("course_render.nav_bar.course_grades")), 
        ("resources", translate("course_render.nav_bar.course_resources"))
    ])

    nav_keys = [k for k, _ in nav_items]
    return nav_keys, nav_items

def _render_about(course_json: dict, request_headers: dict | None = None):
    course = _safe_dict(course_json.get("course"))
    instructors = _safe_list(course_json.get("instructors"))
    grading = _safe_dict(course_json.get("grading"))
    prerequisites = _safe_list(course.get("prerequisites"))
    tags = _safe_list(course.get("tags"))
    overview_md = course_json.get("overview_md", "")
    outcomes = _extract_overview_learnings(overview_md)

    st.markdown(translate("course_render.info_tab.title"))

    left, right = st.columns([2, 1], gap="large")

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{translate("course_render.info_tab.about_course")}</div>', unsafe_allow_html=True)
        if overview_md:
            st.markdown(f'<div class="overview-box">', unsafe_allow_html=True)
            _render_markdown_block(overview_md, request_headers=request_headers)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info(translate("course_render.info_tab.info.no_overview"))
        
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{translate("course_render.info_tab.learnings")}</div>', unsafe_allow_html=True)
        if outcomes:
            for item in outcomes:
                st.markdown(f"- {item}")
        else:
            st.info(translate("course_render.info_tab.info.no_learnings"))
        
        st.markdown("</div>", unsafe_allow_html=True)

        pass_percent = grading.get("pass_percent")
        if pass_percent is not None:
            st.markdown("---")
            st.markdown(translate("course_render.quiz_preview.pass_thresold", pass_percent=pass_percent))

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{translate("course_render.info_tab.tags")}</div>', unsafe_allow_html=True)
        if tags:
            st.markdown("".join([f'<span class="tag-chip">{t}</span>' for t in tags]), unsafe_allow_html=True)
        else:
            st.info(translate("course_render.info_tab.info.no_tags"))
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{translate("course_render.info_tab.prerequisites")}</div>', unsafe_allow_html=True)
        if prerequisites:
            for item in prerequisites:
                st.markdown(f"- {item}")
        else:
            st.info(translate("course_render.info_tab.info.no_prerequisites"))
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">{translate("course_render.info_tab.instructors")}</div>', unsafe_allow_html=True)
        if instructors:
            for inst in instructors:
                with st.container(border=True):
                    st.markdown(f"**{inst.get('name', 'Unknown instructor')}**")
                    if inst.get("bio"):
                        st.caption(inst["bio"])
        else:
            st.info(translate("course_render.info_tab.info.no_instructor_info"))
        st.markdown("</div>", unsafe_allow_html=True)

def _render_overview(course_json: dict, request_headers: dict | None = None):
    course = _safe_dict(course_json.get("course"))
    overview_md = course_json.get("overview_md", "")
    st.markdown(translate("course_render.overview_tab.title"))
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{course.get("title", "Course")} overview</div>', unsafe_allow_html=True)
    _render_markdown_block(overview_md, request_headers=request_headers)
    st.markdown("</div>", unsafe_allow_html=True)

def _render_quiz_preview(quiz: dict):
    meta = _safe_dict(quiz.get("meta"))
    items = _safe_list(quiz.get("items"))

    title = meta.get("title", "Quiz")
    pass_percent = float(meta.get("pass_percent", 70))

    st.markdown(f"### 📝 {title}")
    st.caption(translate("course_render.quiz_preview.pass_thresold", pass_percent=pass_percent))

    if not items:
        st.info(translate("course_render.quiz_preview.info.no_items"))
        return

    for idx, item in enumerate(items, start=1):
        qtype = item.get("type", "")
        prompt = item.get("prompt", "")
        choices = _safe_list(item.get("choices"))

        with st.container(border=True):
            st.markdown(f"**Q{idx}.** {prompt}")
            st.caption(translate("course_render.quiz_preview.type_points", qtype=qtype, points=item.get('points', 1)))

            if qtype in {"mcq", "multi_select"}:
                for choice in choices:
                    is_correct = bool(choice.get("correct"))
                    prefix = "✅" if is_correct else "⬜"
                    st.markdown(f"{prefix} {choice.get('text', '')}")

            elif qtype == "true_false":
                st.markdown(translate("course_render.quiz_preview.correct_answer", answer='true' if bool(item.get('answer')) else 'false'))

            elif qtype == "numeric":
                answer_spec = _safe_dict(item.get("answer"))
                st.markdown(
                    translate("course_render.quiz_preview.target", target=answer_spec.get('value', '—') + f" ± {answer_spec.get('tolerance', 0)}")
                )

            elif qtype in {"short_text", "text", "essay"}:
                st.caption(translate("course_render.quiz_preview.free_text"))

            else:
                st.warning(translate("course_render.quiz_preview.warnings", qtype=qtype))

def _render_misconceptions(module: dict):
    misconceptions = _safe_list(module.get("misconceptions"))
    if not misconceptions:
        st.info(translate("course_render.misconceptions.info.no_misconceptions"))
        return

    for item in misconceptions:
        with st.container(border=True):
            if item.get("misconception"):
                st.markdown(translate("course_render.misconceptions.misconception", misconception=item['misconception']))
            if item.get("correction"):
                st.markdown(translate("course_render.misconceptions.correction", correction=item['correction']))

def _render_practice_preview(module: dict):
    questions = _safe_list(module.get("questions"))
    if not questions:
        st.info(translate("course_render.prac_preview.info.no_practices"))
        return

    for idx, q in enumerate(questions, start=1):
        with st.container(border=True):
            st.markdown(f"**Q{idx}.** {q.get('prompt', '')}")
            ref = q.get("reference_answer")
            if ref:
                with st.expander(translate("course_render.prac_preview.expander")):
                    st.markdown(ref)

def _render_practice_questions(
    module: dict,
    prefix: str,
    api_base: str,
    request_headers: dict,
    auth_headers: dict,
    course_id: int,
    progress_snapshot: dict,
    reasoning_model: str | None
):
    questions = _safe_list(module.get("questions"))
    practice_answers = _safe_dict(progress_snapshot.get("practice_answers"))
    eval_key = _state_key(prefix, "practice_evaluations")
    if eval_key not in st.session_state:
        st.session_state[eval_key] = {}

    if not questions:
        st.info(translate("course_render.prac_questions.info.no_practices"))
        return

    for idx, q in enumerate(questions, start=1):
        qid = q.get("id", f"{module.get('module_id')}-q{idx}")
        answer_key = f"{module.get('module_id')}_{qid}"
        show_key = f"{prefix}_show_answer_{answer_key}"

        with st.container(border=True):
            st.markdown(f"**Q{idx}.** {q.get('prompt', '')}")

            current_answer = practice_answers.get(answer_key, "")
            new_answer = st.text_area(
                translate("course_render.prac_questions.text_area_answers.label"),
                value=current_answer,
                key=f"{prefix}_practice_{answer_key}",
                height=120,
                help=translate("course_render.prac_questions.text_area_answers.help"),
            )
            practice_answers[answer_key] = new_answer

            btn1, btn2, btn3, _ = st.columns([1, 1, 1, 4])

            if btn1.button(
                translate("course_render.prac_questions.hide_show_answer_button.hide_label") if st.session_state.get(show_key, False) else translate("course_render.prac_questions.hide_show_answer_button.show_label"),
                key=f"{prefix}_toggle_answer_{answer_key}",
                type="primary",
                width='stretch'               
            ):
                st.session_state[show_key] = not st.session_state.get(show_key, False)
                snapshot = _save_progress(
                    api_base=api_base,
                    request_headers=request_headers,
                    course_id=course_id,
                    current_nav=None,
                    current_module_id=module.get("module_id"),
                    practice_answers=practice_answers,
                )
                _store_progress_snapshot(prefix, snapshot)
                st.rerun()

            if btn2.button(
                translate("course_render.prac_questions.clear_button.label"),
                key=f"{prefix}_clear_answer_{answer_key}",
                type="primary",
                width='stretch',
                help=translate("course_render.prac_questions.clear_button.help")
            ):
                practice_answers[answer_key] = ""
                st.session_state[eval_key].pop(answer_key, None)
                snapshot = _save_progress(
                    api_base=api_base,
                    request_headers=request_headers,
                    course_id=course_id,
                    current_nav=None,
                    current_module_id=module.get("module_id"),
                    practice_answers=practice_answers,
                )
                
                _store_progress_snapshot(prefix, snapshot)
                st.rerun()

            if btn3.button(
                translate("course_render.prac_questions.evaluate_button.label"),
                key=f"{prefix}_evaluate_answer_{answer_key}",
                type="primary",
                width='stretch',
                help=translate("course_render.prac_questions.evaluate_button.help")
            ):
                if not new_answer.strip():
                    st.warning(translate("course_render.prac_questions.evaluate_button.warning"))
                else:
                    try:
                        with st.spinner(translate("course_render.prac_questions.evaluate_button.spin_evaluate")):
                            out = _evaluate_practice_answer(
                                api_base=api_base,
                                auth_headers=auth_headers,
                                question=q.get("prompt", ""),
                                reference_answer=q.get("reference_answer", ""),
                                user_answer=new_answer,
                                reasoning_model=reasoning_model
                            )
                            
                        st.session_state[eval_key][answer_key] = {
                            "message": out.get("message", ""),
                            "grade": out.get("grade"),
                            "summary": out.get("summary", ""),
                        }

                        snapshot = _save_progress(
                            api_base=api_base,
                            request_headers=request_headers,
                            course_id=course_id,
                            current_nav=None,
                            current_module_id=module.get("module_id"),
                            practice_answers=practice_answers,
                        )
                        
                        _store_progress_snapshot(prefix, snapshot)
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
            
            # --- Evaluation result block ---
            evaluation = _safe_dict(st.session_state.get(eval_key, {})).get(answer_key)
            
            if evaluation:
                grade = evaluation.get("grade")
                summary = evaluation.get("summary", "")
                message = evaluation.get("message", "")

                variant = grade_status_variant(grade)
                grade_text = grade_label(grade)

                if variant == "success":
                    st.success(translate("course_render.prac_questions.success.eval_completed", grade_text=grade_text))
                elif variant == "warning":
                    st.warning(translate("course_render.prac_questions.warning.eval_completed", grade_text=grade_text))
                elif variant == "error":
                    st.error(translate("course_render.prac_questions.error.eval_completed", grade_text=grade_text))
                else:
                    st.info(translate("course_render.prac_questions.info.eval_completed", grade_text=grade_text))

                if message and message != "success":
                    st.caption(message)

                if summary:
                    with st.expander(
                        translate("course_render.prac_questions.expander.evaluation"),
                        expanded=True,
                    ):
                        st.markdown(summary)
            
            # --- Suggested answer block ---
            if st.session_state.get(show_key, False):
                with st.expander(translate("course_render.prac_questions.expander.suggested_answer"), expanded=True):
                    st.markdown(q.get("reference_answer", "—"))

def _render_quiz_interactive(
    quiz: dict,
    prefix: str,
    result_key: str,
    api_base: str,
    auth_headers: dict,
    course_id: int,
    assessment_type: str,
    module_id: str,
    progress_snapshot: dict,
    reasoning_model: str | None,
    is_enrolled: bool,
):
    meta = _safe_dict(quiz.get("meta"))
    items = _safe_list(quiz.get("items"))

    title = meta.get("title", "Quiz")
    assessment_id = meta.get("id", "")
    pass_percent = float(meta.get("pass_percent", 70))

    st.markdown(f"### 📝 {title}")
    st.caption(translate("course_render.quiz_interactive.pass_thresold", pass_percent=pass_percent))

    if not is_enrolled:
        st.warning(translate("course_render.quiz_interactive.not_enrolled"))
        return
    
    if not items:
        st.info(translate("course_render.quiz_interactive.info.no_quiz"))
        return
    
    if assessment_type == "final_quiz":
        allowed, reason = _can_attempt_final_quiz(
            _safe_dict(st.session_state[_state_key(prefix, "course_json")]),
            progress_snapshot,
        )
        if not allowed:
            st.warning(reason)
    
    answers_payload: list[dict] = []
    
    with st.form(key=f"{prefix}_quiz_form_{result_key}"):
        for idx, item in enumerate(items, start=1):
            item_id = item.get("id", f"q{idx}")
            qtype = item.get("type", "")
            prompt = item.get("prompt", "")
            choices = _safe_list(item.get("choices"))

            st.markdown(f"**Q{idx}.** {prompt}")

            if qtype == "mcq":
                select_options = [
                    {
                        "label": "— Select an answer —", 
                        "value": None
                    }
                ]

                for c in choices:
                    select_options.append({"label": c.get("text", ""), "value": c.get("id")})

                selected_label = st.selectbox(
                    " ",
                    options=[opt["label"] for opt in select_options],
                    index=0,
                    key=f"{prefix}_{result_key}_{item_id}",
                    label_visibility="collapsed",
                )

                selected_value = next(
                    (opt["value"] for opt in select_options if opt["label"] == selected_label),
                    None,
                )

                answers_payload.append(
                    {
                        "item_id": item_id,
                        "selected_choice_ids": [selected_value] if selected_value else [],
                    }
                )

            elif qtype == "multi_select":
                labels = [c.get("text", "") for c in choices]
                selected_labels = st.multiselect(
                    " ",
                    options=labels,
                    default=[],
                    key=f"{prefix}_{result_key}_{item_id}",
                    label_visibility="collapsed",
                )
                selected_ids = [c.get("id") for c in choices if c.get("text", "") in selected_labels]
                answers_payload.append(
                    {
                        "item_id": item_id,
                        "selected_choice_ids": selected_ids,
                    }
                )

            elif qtype == "true_false":
                selected_tf = st.selectbox(
                    " ",
                    options=["— Select —", "true", "false"],
                    index=0,
                    key=f"{prefix}_{result_key}_{item_id}",
                    label_visibility="collapsed",
                )
                answers_payload.append(
                    {
                        "item_id": item_id,
                        "selected_value": None if selected_tf == "— Select —" else selected_tf,
                    }
                )

            elif qtype == "numeric":
                raw_value = st.text_input(
                    " ",
                    value="",
                    key=f"{prefix}_{result_key}_{item_id}",
                    label_visibility="collapsed",
                )
                answers_payload.append(
                    {
                        "item_id": item_id,
                        "selected_value": raw_value if raw_value.strip() else None,
                    }
                )

            elif qtype in {"short_text", "text", "essay"}:
                raw_text = st.text_area(
                    translate("course_render.quiz_interactive.text_area_response.label"),
                    key=f"{prefix}_{result_key}_{item_id}",
                    height=120,
                    label_visibility="collapsed",
                )
                answers_payload.append(
                    {
                        "item_id": item_id,
                        "selected_value": raw_text,
                    }
                )

            else:
                st.warning(translate("course_render.quiz_interactive.warning", qtype=qtype))

            st.divider()
        
        submit_disabled = (
            assessment_type == "final_quiz"
            and not _can_attempt_final_quiz(
                _safe_dict(st.session_state[_state_key(prefix, "course_json")]),
                progress_snapshot,
            )[0]
        )
        
        submitted = st.form_submit_button(
            translate("course_render.quiz_interactive.submit_button.label"),
            type="primary",
            disabled=submit_disabled,
            help=translate("course_render.quiz_interactive.submit_button.help")
        )
    
    result_store_key = _state_key(prefix, f"{result_key}_result")
    
    if submitted:
        try:
            with st.spinner(translate("course_render.quiz_interactive.submit_button.spinner")):
                response = _submit_quiz_attempt(
                    api_base=api_base,
                    auth_headers=auth_headers,
                    course_id=course_id,
                    assessment_type=assessment_type,
                    module_id=module_id,
                    assessment_id=assessment_id,
                    answers=answers_payload,
                    reasoning_model=reasoning_model,
                )
            
            result = response.get("result") or {}
            st.session_state[result_store_key] = result
            _store_progress_snapshot(prefix, response.get("progress_snapshot") or {})
            st.rerun()
        except Exception as e:
            st.error(str(e))
        
    stored_result = _safe_dict(st.session_state.get(result_store_key))
    
    if stored_result:
        score = float(stored_result.get("score", 0) or 0)
        total_points = float(stored_result.get("total_points", 0) or 0)
        percent = float(stored_result.get("percent", 0) or 0)
        german_grade = stored_result.get("german_grade", "—")

        message = translate(
            "course_render.quiz_interactive.grading_text.result_message",
            score=f"{score:.1f}",
            total_points=f"{total_points:.1f}",
            percent=f"{percent:.0f}",
            status=translate(
                "course_render.quiz_interactive.grading_text.result_passed"
                if stored_result.get("passed")
                else "course_render.quiz_interactive.grading_text.result_failed"
            ),
            german_grade=german_grade,
        )

        if stored_result.get("passed"):
            st.success(message)
        else:
            st.error(message)
        
        feedback = _safe_list(stored_result.get("feedback"))
        
        if feedback:
            with st.expander(translate("course_render.quiz_interactive.submit_button.expander"), expanded=True):
                for idx, item_feedback in enumerate(feedback, start=1):
                    print(f"ℹ️ Getting the feedbacks: {item_feedback}")
                    with st.container(border=True):
                        st.markdown(f"**Item {idx}.** {item_feedback.get('prompt', '')}")
                        st.caption(
                            f"Awarded: {item_feedback.get('awarded_points', 0)}/{item_feedback.get('max_points', 0)} "
                            f"· Type: {item_feedback.get('type', '—')}"
                        )
                        
                        if item_feedback.get("grade") is not None:
                            st.markdown(f"**LLM Grade:** {item_feedback.get('grade')}")
                        if item_feedback.get("summary"):
                            st.markdown(item_feedback.get("summary"))

def _render_gradebook(
    course_json: dict, 
    progress_snapshot: dict,
    is_enrolled: bool,
):
    if not is_enrolled:
        st.markdown(translate("course_render.gradebook.title"))
        st.info(translate("course_render.gradebook.info.enroll_message"))
        return
    
    grading = _safe_dict(course_json.get("grading"))
    modules = _safe_list(course_json.get("modules"))
    final_quiz = _safe_dict(course_json.get("final_quiz"))

    progress_snapshot = _normalize_progress_snapshot(progress_snapshot)
    
    module_status = _safe_dict(progress_snapshot.get("module_status"))
    final_status = _safe_dict(progress_snapshot.get("final_status"))
    course_completion = _safe_dict(progress_snapshot.get("course_completion"))

    st.markdown(translate("course_render.gradebook.title"))
    
    course_pass = float(grading.get("pass_percent", 70))
    assessment_weights = _safe_dict(grading.get("assessment_weights"))

    weighted_sum = 0.0
    weight_total = 0.0
    rows = []

    for module in modules:
        module_id = str(module.get("module_id"))
        status = _safe_dict(module_status.get(module_id))
        percent = status.get("best_percent")
        passed = bool(status.get("quiz_passed"))
        weight = float(assessment_weights.get(module_id, 0.0))

        if percent is not None:
            weighted_sum += float(percent) * weight
            weight_total += weight

        rows.append(
            {
                "title": module.get("title", module_id),
                "weight": weight,
                "percent": percent,
                "passed": passed,
                "german_grade": status.get("best_german_grade") or status.get("last_german_grade"),
            }
        )

    if final_quiz.get("items"):
        final_percent = final_status.get("best_percent")
        final_passed = bool(final_status.get("passed"))
        final_weight = float(assessment_weights.get("final_quiz", 0.0))

        if final_percent is not None:
            weighted_sum += float(final_percent) * final_weight
            weight_total += final_weight

        rows.append(
            {
                "title": (_safe_dict(final_quiz.get("meta")).get("title") or "Final quiz"),
                "weight": final_weight,
                "percent": final_percent,
                "passed": final_passed,
                "german_grade": final_status.get("best_german_grade") or final_status.get("last_german_grade"),
            }
        )

    course_grade_percent = course_completion.get("weighted_percent")
    course_grade_de = course_completion.get("german_grade")

    if course_grade_percent is None and weight_total > 0:
        course_grade_percent = weighted_sum / weight_total

    if course_grade_percent is None:
        st.info(translate("course_render.gradebook.info.no_graded_attempt"))
    else:
        st.metric(translate("course_render.gradebook.weighted_grade"), f"{course_grade_percent:.0f}%")
        st.caption(f"German grade: {course_grade_de if course_grade_de is not None else '—'}")

        if course_grade_percent >= course_pass:
            st.success(translate("course_render.gradebook.grade_met", course_pass=course_pass))
        else:
            st.warning(translate("course_render.gradebook.grade_not_met", course_pass=course_pass))

    completion_status = str(course_completion.get("status") or "")
    
    if course_completion.get("completed"):
        st.success(translate("course_render.gradebook.info.course_completed"))
    elif completion_status == "eligible_for_final_quiz":
        st.info(translate("course_render.gradebook.info.eligible_final_quiz"))
    elif completion_status:
        st.info(translate("course_render.gradebook.info.course_completed_status", status=completion_status))
    
    for row in rows:
        with st.container(border=True):
            left, mid, right, extra = st.columns([5, 2, 2, 2])
            left.markdown(f"**{row['title']}**")
            mid.markdown(f"{row['weight'] * 100:.0f}%")

            if row["percent"] is None:
                right.markdown(translate("course_render.gradebook.result.not_attempted"))
            elif row["passed"]:
                right.markdown(translate("course_render.gradebook.result.passed", row=row["percent"]))
            else:
                right.markdown(translate("course_render.gradebook.result.failed", row=row["percent"]))
            
            extra.markdown(str(row["german_grade"]) if row["german_grade"] is not None else "—")

def _render_resources(course_json: dict):
    resources = _safe_list(course_json.get("resources"))
    st.markdown(translate("course_render.resources.title"))
    if not resources:
        st.info(translate("course_render.resources.info"))
        return

    for r in resources:
        with st.container(border=True):
            st.markdown(f"**{r.get('title', 'Untitled')}**")
            if r.get("type"):
                st.caption(r["type"])
            if r.get("url"):
                st.markdown(r["url"])

def _render_module(
    module: dict,
    mode: RenderMode,
    prefix: str,
    api_base: str | None = None,
    request_headers: dict | None = None,
    auth_headers: dict | None = None,
    course_id: int | None = None,
    progress_snapshot: dict | None = None,
    reasoning_model: str | None = None,
    is_enrolled: bool = False,
):
    st.markdown(f"## 📘 {module.get('title', 'Untitled module')}")
    
    tab_labels = [
        translate("course_render.modules_sub.tabs.content"),
        translate("course_render.modules_sub.tabs.practice"),
        translate("course_render.modules_sub.tabs.quiz"),
        translate("course_render.modules_sub.tabs.reading"),
        translate("course_render.modules_sub.tabs.misconceptions")
    ]
    
    if mode == "instructor_preview":
        tab_labels.append(translate("course_render.modules_sub.tabs.meta"))
    
    tab_objs = st.tabs(tab_labels)
        
    with tab_objs[0]:
        _render_markdown_block(module.get("content_md"), request_headers=request_headers)

    with tab_objs[1]:
        if mode == "learner":
            if not is_enrolled:
                st.info(translate("course_render.modules_sub.info.enroll_for_practice"))
            elif api_base and course_id and request_headers and auth_headers:
                _render_practice_questions(
                    module=module,
                    prefix=prefix,
                    api_base=api_base,
                    request_headers=request_headers,
                    auth_headers=auth_headers,
                    course_id=course_id,
                    progress_snapshot=_safe_dict(progress_snapshot),
                    reasoning_model=reasoning_model
                )
            
            else:
                st.info(translate("course_render.modules_sub.info.prac_no"))
        else:
            _render_practice_preview(module)

    with tab_objs[2]:
        if mode == "learner":
            if not is_enrolled:
                st.info(translate("course_render.modules_sub.info.enroll_for_quiz"))
            elif api_base and course_id and auth_headers:
                _render_quiz_interactive(
                    quiz=_safe_dict(module.get("quiz")),
                    prefix=prefix,
                    result_key=f"quiz_{module.get('module_id')}",
                    api_base=api_base,
                    auth_headers=auth_headers,
                    course_id=course_id,
                    assessment_type="module_quiz",
                    module_id=module.get("module_id"),
                    progress_snapshot=_safe_dict(progress_snapshot),
                    reasoning_model=reasoning_model,
                    is_enrolled=is_enrolled,
                )
            else:
                st.info(translate("course_render.modules_sub.info.quiz_no"))
        else:
            _render_quiz_preview(_safe_dict(module.get("quiz")))

    with tab_objs[3]:
        _render_markdown_block(module.get("further_reading_md"), request_headers=request_headers)

    with tab_objs[4]:
        _render_misconceptions(module)

    if mode != "learner":
        with tab_objs[5]:
            st.json(
                {
                    "module_id": module.get("module_id"),
                    "grade": module.get("grade"),
                    "question_count": len(_safe_list(module.get("questions"))),
                    "quiz_meta": _safe_dict(_safe_dict(module.get("quiz")).get("meta")),
                }
            )

def render_course_experience(
    course_json: Dict[str, Any],
    mode: RenderMode = "learner",
    state_prefix: str = "course",
    show_sidebar_nav: bool = True,
    api_base: str | None = None,
    request_headers: dict | None = None,
    auth_headers: dict | None = None,
    course_id: int | None = None,
    progress_snapshot: dict | None = None,
    attempt_summaries: dict | None = None,
    reasoning_model_name: str | None = None,
    is_enrolled: bool = False,
):
    inject_course_styles()

    modules = _safe_list(course_json.get("modules"))
    final_quiz = _safe_dict(course_json.get("final_quiz"))

    nav_key = _state_key(state_prefix, "nav")
    course_key = _state_key(state_prefix, "course_json")
    st.session_state[course_key] = course_json

    current_progress = _initialize_progress_state(state_prefix, progress_snapshot, is_enrolled)

    current_progress = _normalize_progress_snapshot(current_progress, is_enrolled=is_enrolled)
    
    nav_keys, nav_items = _render_sidebar(course_json, state_prefix)
    nav_labels = [label for _, label in nav_items]

    if st.session_state.get(nav_key) not in nav_keys:
        st.session_state[nav_key] = current_progress.get("current_nav") or "overview"

    _render_hero(course_json, mode=mode, progress_snapshot=current_progress)

    nav_col, main_col = st.columns([1.05, 2.95], gap="large")

    with nav_col:
        st.markdown('<div class="curriculum-card">', unsafe_allow_html=True)
        st.markdown(translate("course_render.render_experience.nav_col_title"))
        selected_label = st.radio(
            " ",
            nav_labels,
            index=nav_keys.index(st.session_state[nav_key]),
            label_visibility="collapsed",
            key=_state_key(state_prefix, "nav_radio"),
        )
        selected_nav = nav_keys[nav_labels.index(selected_label)]

        if selected_nav != st.session_state[nav_key]:
            st.session_state[nav_key] = selected_nav

            if mode == "learner" and api_base and course_id and request_headers and is_enrolled:
                current_module_id = None
                if selected_nav.startswith("module_"):
                    try:
                        selected_idx = int(selected_nav.split("_")[1])
                        if 0 <= selected_idx < len(modules):
                            current_module_id = modules[selected_idx].get("module_id")
                    except Exception:
                        pass

                snapshot = _save_progress(
                    api_base=api_base,
                    request_headers=request_headers,
                    course_id=course_id,
                    current_nav=selected_nav,
                    current_module_id=current_module_id,
                    practice_answers=current_progress.get("practice_answers") or {},
                )
                _store_progress_snapshot(state_prefix, snapshot)

            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with main_col:
        page = st.session_state[nav_key]

        if page == "overview":
            _render_overview(course_json, request_headers=request_headers)

        elif page == "about":
            _render_about(course_json, request_headers=request_headers)

        elif page.startswith("module_"):
            module_idx = int(page.split("_")[1])
            if not (0 <= module_idx < len(modules)):
                st.warning("Invalid module selection.")
            else:
                _render_module(
                    module=modules[module_idx],
                    mode=mode,
                    prefix=state_prefix,
                    api_base=api_base,
                    request_headers=request_headers,
                    auth_headers=auth_headers,
                    course_id=course_id,
                    progress_snapshot=current_progress,
                    reasoning_model=reasoning_model_name,
                    is_enrolled=is_enrolled
                )

        elif page == "final_quiz":
            st.markdown(translate("course_render.render_experience.final_ass_title"))
            if mode == "learner":
                if not is_enrolled:
                    st.info(translate("course_render.modules_sub.info.enroll_for_final_quiz"))
                elif api_base and course_id and auth_headers:
                    _render_quiz_interactive(
                        quiz=final_quiz,
                        prefix=state_prefix,
                        result_key="quiz_final",
                        api_base=api_base,
                        auth_headers=auth_headers,
                        course_id=course_id,
                        assessment_type="final_quiz",
                        module_id=None,
                        progress_snapshot=current_progress,
                        reasoning_model=reasoning_model_name,
                        is_enrolled=is_enrolled
                    )
                else:
                    st.info(translate("course_render.render_experience.final_quiz_intera_info"))
            else:
                _render_quiz_preview(final_quiz)

        elif page == "grades":
            _render_gradebook(course_json, current_progress, is_enrolled)

        elif page == "resources":
            _render_resources(course_json)
