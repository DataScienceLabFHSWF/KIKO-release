# backend/app/services/learner_course_progress_service.py
import asyncio
from typing import Any
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.models import CourseModel
from app.models import LearnerCourseProgressModel, LearnerQuizAttemptModel
from .answer_grading_service import grade_user_answer
from copy import deepcopy
from sqlalchemy.orm.attributes import flag_modified

DEFAULT_GERMAN_SCALE = [
    {"min_percent": 95, "grade": 1.0},
    {"min_percent": 90, "grade": 1.3},
    {"min_percent": 85, "grade": 1.7},
    {"min_percent": 80, "grade": 2.0},
    {"min_percent": 75, "grade": 2.3},
    {"min_percent": 70, "grade": 2.7},
    {"min_percent": 65, "grade": 3.0},
    {"min_percent": 60, "grade": 3.3},
    {"min_percent": 55, "grade": 3.7},
    {"min_percent": 50, "grade": 4.0},
    {"min_percent": 0, "grade": 5.0},
]

DEFAULT_FREE_TEXT_CREDIT_RATIOS = {
    1: 1.00,
    2: 0.85,
    3: 0.70,
    4: 0.50,
    5: 0.00,
}

def _safe_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}

def _safe_list(value: Any) -> list:
    return value if isinstance(value, list) else []

def _default_course_completion() -> dict:
    return {
        "status": "in_progress",
        "eligible_for_final_quiz": False,
        "completed": False,
        "weighted_percent": None,
        "german_grade": None,
    }

def _default_progress_json() -> dict:
    return {
        "module_status": {},
        "final_status": {},
        "practice_answers": {},
        "course_completion": _default_course_completion(),
    }

def _normalize_progress_json(src: dict | None) -> dict:
    src = _safe_dict(src)

    return {
        "module_status": _safe_dict(src.get("module_status")),
        "final_status": _safe_dict(src.get("final_status")),
        "practice_answers": _safe_dict(src.get("practice_answers")),
        "course_completion": {
            **_default_course_completion(),
            **_safe_dict(src.get("course_completion")),
        },
    }

def _assign_progress_json(progress, progress_json: dict) -> None:
    progress.progress_json = deepcopy(_normalize_progress_json(progress_json))
    flag_modified(progress, "progress_json")

def german_grade_from_percent(
    percent: float, 
    scale: list[dict] | None = None
) -> float:
    use_scale = scale or DEFAULT_GERMAN_SCALE
    for row in sorted(use_scale, key=lambda x: x["min_percent"], reverse=True):
        if percent >= float(row["min_percent"]):
            return float(row["grade"])
    return 5.0

def free_text_credit_ratio_from_grade(
    grade: int,
    ratios: dict[int, float] | None = None,
) -> float:
    use_ratios = ratios or DEFAULT_FREE_TEXT_CREDIT_RATIOS
    return float(use_ratios.get(int(grade), 0.0))

async def get_or_create_progress(
    course_id: int,
    learner_user_id: int,
    db: AsyncSession,
) -> LearnerCourseProgressModel:
    try:
        result = await db.execute(
            select(LearnerCourseProgressModel)
            .where(
                LearnerCourseProgressModel.course_id == course_id,
                LearnerCourseProgressModel.learner_user_id == learner_user_id,
            )
        )
        
        progress = result.scalar_one_or_none()

        if progress:
            return progress

        progress = LearnerCourseProgressModel(
            course_id=course_id,
            learner_user_id=learner_user_id,
            current_nav="overview",
            current_module_id=None,
            completion_percent=0.0,
            progress_json={
                "module_status": {},
                "final_status": {},
                "practice_answers": {},
                "course_completion": {
                    "status": "in_progress",
                    "eligible_for_final_quiz": False,
                    "completed": False,
                    "weighted_percent": None,
                    "german_grade": None,
                },
            },
        )
        
        db.add(progress)
        await db.flush()
        return progress
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error: {str(e)}"
        )

async def get_course_with_json(
    course_id: int, 
    db: AsyncSession
) -> CourseModel:
    
    result = await db.execute(
        select(CourseModel)
        .where(
            CourseModel.course_id == course_id
        )
    )
    
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="❌ Course not found",
        )

    if not isinstance(course.course_json, dict) or not course.course_json:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="❌ Course does not have structured course_json",
        )

    return course

def find_module(
    course_json: dict, 
    module_id: str
) -> dict | None:
    for module in _safe_list(course_json.get("modules")):
        if module.get("module_id") == module_id:
            return module
    return None

def get_module_quiz(
    course_json: dict, 
    module_id: str, 
    assessment_id: str
) -> tuple[dict, dict]:
    module = find_module(course_json, module_id)
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_id}' not found",
        )

    quiz = _safe_dict(module.get("quiz"))
    meta = _safe_dict(quiz.get("meta"))
    quiz_id = meta.get("id")

    if not quiz_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_id}' has no quiz id",
        )

    if quiz_id != assessment_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment '{assessment_id}' not found in module '{module_id}'",
        )

    return module, quiz

def get_final_quiz(
    course_json: dict, 
    assessment_id: str
) -> dict:
    quiz = _safe_dict(course_json.get("final_quiz"))
    meta = _safe_dict(quiz.get("meta"))
    quiz_id = meta.get("id")

    if not quiz.get("items"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Final quiz not found",
        )

    if not quiz_id or quiz_id != assessment_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Final assessment '{assessment_id}' not found",
        )

    return quiz

def get_pass_percent_for_assessment(
    course_json: dict,
    quiz: dict,
    module: dict | None = None,
) -> float:
    quiz_meta = _safe_dict(quiz.get("meta"))
    
    if quiz_meta.get("pass_percent") is not None:
        return float(quiz_meta.get("pass_percent"))

    if module:
        module_grade = _safe_dict(module.get("grade"))
        if module_grade.get("pass_percent") is not None:
            return float(module_grade.get("pass_percent"))

    grading = _safe_dict(course_json.get("grading"))
    completion = _safe_dict(_safe_dict(grading.get("policy")).get("completion"))

    if completion.get("assessment_pass_percent") is not None:
        return float(completion.get("assessment_pass_percent"))
    if grading.get("pass_percent") is not None:
        return float(grading.get("pass_percent"))

    return 70.0

def get_module_quiz_pass_percent(
    course_json: dict, 
    module: dict, quiz: dict
) -> float:
    quiz_meta = _safe_dict(quiz.get("meta"))
    module_grade = _safe_dict(module.get("grade"))
    course_grading = _safe_dict(course_json.get("grading"))
    completion = _safe_dict(_safe_dict(course_grading.get("policy")).get("completion"))

    if quiz_meta.get("pass_percent") is not None:
        return float(quiz_meta.get("pass_percent"))
    if module_grade.get("pass_percent") is not None:
        return float(module_grade.get("pass_percent"))
    if completion.get("assessment_pass_percent") is not None:
        return float(completion.get("assessment_pass_percent"))
    if course_grading.get("pass_percent") is not None:
        return float(course_grading.get("pass_percent"))
    return 70.0

def normalize_answers_by_item(answers: list[dict]) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for answer in answers or []:
        item_id = str(answer.get("item_id") or "").strip()
        if item_id:
            result[item_id] = answer
    return result

async def grade_text_items(
    items: list[dict],
    answers_by_item: dict[str, dict],
    reasoning_model_name: str | None,
    response_language: str,
) -> dict[str, dict]:
    tasks = []
    task_meta = []

    for item in items:
        qtype = str(item.get("type") or "")
        if qtype not in {"short_text", "text", "essay"}:
            continue

        item_id = str(item.get("id") or "")
        submitted = answers_by_item.get(item_id, {})
        user_answer = str(submitted.get("selected_value") or "").strip()
        reference_answer = str(item.get("answer") or item.get("reference_answer") or "").strip()
        prompt = str(item.get("prompt") or "").strip()

        if not item_id:
            continue

        if not user_answer:
            task_meta.append(("empty", item_id))
            continue

        tasks.append(
            grade_user_answer(
                question=prompt,
                user_answer=user_answer,
                inference_model_name=reasoning_model_name,
                reference_answer=reference_answer,
                no_max_tokens=1024,
                response_language=response_language,
            )
        )
        task_meta.append(("llm", item_id))

    results_map: dict[str, dict] = {}

    llm_results = await asyncio.gather(*tasks, return_exceptions=True) if tasks else []
    llm_idx = 0

    for mode, item_id in task_meta:
        if mode == "empty":
            results_map[item_id] = {
                "grade": 5,
                "summary": "No answer submitted.",
            }
        else:
            result = llm_results[llm_idx]
            llm_idx += 1

            if isinstance(result, Exception):
                results_map[item_id] = {
                    "grade": 5,
                    "summary": f"Failed to grade this answer: {str(result)}",
                }
            else:
                results_map[item_id] = {
                    "grade": int(result.get("grade", 5)),
                    "summary": result.get("summary", ""),
                }

    return results_map

async def grade_quiz(
    course_json: dict,
    quiz: dict,
    answers: list[dict],
    response_language: str,
    reasoning_model_name: str | None = None,
    module: dict | None = None,
) -> dict:
    items = _safe_list(quiz.get("items"))
    answers_by_item = normalize_answers_by_item(answers)
    pass_percent = get_pass_percent_for_assessment(course_json, quiz, module)

    text_results = await grade_text_items(
        items=items,
        answers_by_item=answers_by_item,
        reasoning_model_name=reasoning_model_name,
        response_language=response_language,
    )

    total_points = 0.0
    score = 0.0
    feedback = []

    for item in items:
        item_id = str(item.get("id") or "")
        qtype = str(item.get("type") or "")
        points = float(item.get("points", 1))
        prompt = str(item.get("prompt") or "")
        total_points += points

        submitted = answers_by_item.get(item_id, {})
        item_feedback = {
            "item_id": item_id,
            "prompt": prompt,
            "type": qtype,
            "awarded_points": 0.0,
            "max_points": points,
            "correct": False,
            "summary": None,
            "grade": None,
        }

        if qtype == "mcq":
            selected_ids = set(submitted.get("selected_choice_ids") or [])
            correct_ids = {
                c.get("id")
                for c in _safe_list(item.get("choices"))
                if c.get("correct") is True
            }
            if selected_ids == correct_ids:
                score += points
                item_feedback["awarded_points"] = points
                item_feedback["correct"] = True

        elif qtype == "multi_select":
            selected_ids = set(submitted.get("selected_choice_ids") or [])
            correct_ids = {
                c.get("id")
                for c in _safe_list(item.get("choices"))
                if c.get("correct") is True
            }
            if selected_ids == correct_ids:
                score += points
                item_feedback["awarded_points"] = points
                item_feedback["correct"] = True

        elif qtype == "true_false":
            selected_value = submitted.get("selected_value")
            selected_bool = str(selected_value).lower() == "true"
            if selected_bool == bool(item.get("answer")):
                score += points
                item_feedback["awarded_points"] = points
                item_feedback["correct"] = True

        elif qtype == "numeric":
            raw_value = submitted.get("selected_value")
            try:
                submitted_num = float(raw_value)
                answer_spec = _safe_dict(item.get("answer"))
                target = float(answer_spec.get("value", 0.0))
                tolerance = float(answer_spec.get("tolerance", 0.0))
                if abs(submitted_num - target) <= tolerance:
                    score += points
                    item_feedback["awarded_points"] = points
                    item_feedback["correct"] = True
            except Exception:
                pass

        elif qtype in {"short_text", "text", "essay"}:
            text_result = _safe_dict(text_results.get(item_id))
            grade = int(text_result.get("grade", 5))
            summary = text_result.get("summary", "")
            ratio = free_text_credit_ratio_from_grade(grade)

            awarded = round(points * ratio, 2)
            score += awarded

            item_feedback["awarded_points"] = awarded
            item_feedback["correct"] = grade in (1, 2)
            item_feedback["summary"] = summary
            item_feedback["grade"] = grade

        else:
            item_feedback["summary"] = f"Unsupported item type '{qtype}'"

        feedback.append(item_feedback)

    percent = 0.0 if total_points == 0 else round((score / total_points) * 100.0, 2)
    passed = percent >= pass_percent

    grading = _safe_dict(course_json.get("grading"))
    scale = _safe_list(_safe_dict(grading.get("policy")).get("grade_scale"))
    german_grade = german_grade_from_percent(percent, scale if scale else None)

    return {
        "score": score,
        "total_points": total_points,
        "percent": percent,
        "passed": passed,
        "pass_percent": pass_percent,
        "german_grade": german_grade,
        "feedback": feedback,
    }

def can_attempt_final_quiz(
    course_json: dict, 
    progress_json: dict
) -> tuple[bool, str | None]:
    
    grading = _safe_dict(course_json.get("grading"))
    completion = _safe_dict(_safe_dict(grading.get("policy")).get("completion"))
    required_modules = _safe_list(completion.get("required_modules"))

    if not required_modules:
        required_modules = [m.get("module_id") for m in _safe_list(course_json.get("modules")) if m.get("module_id")]

    module_status = _safe_dict(progress_json.get("module_status"))
    missing = []

    for module_id in required_modules:
        if not _safe_dict(module_status.get(module_id)).get("quiz_passed"):
            missing.append(module_id)

    if missing:
        return False, f"Required module quizzes not yet passed: {', '.join(missing)}"

    return True, None

def compute_weighted_course_percent(
    course_json: dict, 
    progress_json: dict
) -> float | None:
    grading = _safe_dict(course_json.get("grading"))
    weights = _safe_dict(grading.get("assessment_weights"))
    module_status = _safe_dict(progress_json.get("module_status"))
    final_status = _safe_dict(progress_json.get("final_status"))

    weighted_sum = 0.0
    weight_total = 0.0

    modules = _safe_list(course_json.get("modules"))
    for module in modules:
        module_id = module.get("module_id")
        best_percent = _safe_dict(module_status.get(module_id)).get("best_percent")
        if best_percent is None:
            continue

        weight = float(weights.get(module_id, 0.0))
        if weight <= 0:
            continue

        weighted_sum += float(best_percent) * weight
        weight_total += weight

    final_best = final_status.get("best_percent")
    if final_best is not None:
        final_weight = float(weights.get("final_quiz", 0.0))
        if final_weight > 0:
            weighted_sum += float(final_best) * final_weight
            weight_total += final_weight

    if weight_total > 0:
        return round(weighted_sum / weight_total, 2)

    values = []
    for module in modules:
        module_id = module.get("module_id")
        best_percent = _safe_dict(module_status.get(module_id)).get("best_percent")
        if best_percent is not None:
            values.append(float(best_percent))

    if final_best is not None:
        values.append(float(final_best))

    if not values:
        return None

    return round(sum(values) / len(values), 2)

def compute_course_completion(course_json: dict, progress_json: dict) -> dict:
    grading = _safe_dict(course_json.get("grading"))
    completion = _safe_dict(_safe_dict(grading.get("policy")).get("completion"))
    module_status = _safe_dict(progress_json.get("module_status"))
    final_status = _safe_dict(progress_json.get("final_status"))

    required_modules = _safe_list(completion.get("required_modules"))
    if not required_modules:
        required_modules = [m.get("module_id") for m in _safe_list(course_json.get("modules")) if m.get("module_id")]

    required_assessments = _safe_list(completion.get("required_assessments"))
    if not required_assessments:
        if _safe_dict(course_json.get("final_quiz")).get("items"):
            required_assessments = ["final_quiz"]

    eligible_for_final_quiz, _ = can_attempt_final_quiz(course_json, progress_json)

    required_modules_passed = all(
        _safe_dict(module_status.get(module_id)).get("quiz_passed") for module_id in required_modules
    ) if required_modules else True

    required_assessments_passed = True
    if "final_quiz" in required_assessments:
        required_assessments_passed = bool(final_status.get("passed"))

    weighted_percent = compute_weighted_course_percent(course_json, progress_json)
    course_pass_percent = float(
        completion.get("assessment_pass_percent")
        or grading.get("pass_percent")
        or 70.0
    )

    completed = (
        required_modules_passed
        and required_assessments_passed
        and weighted_percent is not None
        and weighted_percent >= course_pass_percent
    )

    if completed:
        status_value = "completed"
    elif eligible_for_final_quiz:
        status_value = "eligible_for_final_quiz"
    else:
        status_value = "in_progress"

    german_grade = german_grade_from_percent(weighted_percent) if weighted_percent is not None else None

    return {
        "status": status_value,
        "eligible_for_final_quiz": eligible_for_final_quiz,
        "completed": completed,
        "weighted_percent": weighted_percent,
        "course_pass_percent": course_pass_percent,
        "german_grade": german_grade,
        "required_modules": required_modules,
        "required_assessments": required_assessments,
    }

def build_progress_snapshot(progress: LearnerCourseProgressModel) -> dict:
    progress_json = _normalize_progress_json(progress.progress_json)
    return {
        "current_nav": progress.current_nav or "overview",
        "current_module_id": progress.current_module_id,
        "completion_percent": float(progress.completion_percent or 0.0),
        "module_status": progress_json["module_status"],
        "final_status": progress_json["final_status"],
        "practice_answers": progress_json["practice_answers"],
        "course_completion": progress_json["course_completion"],
    }

def build_attempt_summaries(progress_json: dict) -> dict:
    return {
        "module_quizzes": _safe_dict(progress_json.get("module_status")),
        "final_quiz": _safe_dict(progress_json.get("final_status")),
        "course_completion": _safe_dict(progress_json.get("course_completion")),
    }

def compute_completion_percent(
    course_json: dict, 
    progress_json: dict
) -> float:
    modules = _safe_list(course_json.get("modules"))
    module_status = _safe_dict(progress_json.get("module_status"))
    final_quiz = _safe_dict(course_json.get("final_quiz"))
    final_status = _safe_dict(progress_json.get("final_status"))

    total = len(modules) + (1 if final_quiz.get("items") else 0)
    if total == 0:
        return 0.0

    completed = 0
    for module in modules:
        module_id = module.get("module_id")
        if _safe_dict(module_status.get(module_id)).get("quiz_passed"):
            completed += 1

    if final_quiz.get("items") and final_status.get("passed"):
        completed += 1

    return round((completed / total) * 100.0, 2)

async def update_progress_snapshot(
    course_id: int,
    learner_user_id: int,
    current_nav: str | None,
    current_module_id: str | None,
    practice_answers: dict | None,
    db: AsyncSession,
) -> dict:
    
    progress = await get_or_create_progress(course_id, learner_user_id, db)
    
    progress_json = _normalize_progress_json(deepcopy(progress.progress_json))
    
    if isinstance(current_nav, str):
        progress.current_nav = current_nav

    if current_module_id is None or isinstance(current_module_id, str):
        progress.current_module_id = current_module_id

    if isinstance(practice_answers, dict):
        progress_json["practice_answers"] = practice_answers

    _assign_progress_json(progress, progress_json)

    await db.commit()
    await db.refresh(progress)

    return build_progress_snapshot(progress)

async def grade_text_quiz_items(
    items: list[dict],
    answers_by_item: dict[str, dict],
    reasoning_model_name: str | None,
    response_language: str,
) -> dict[str, dict]:
    tasks = []
    task_meta = []

    for item in items:
        qtype = str(item.get("type") or "")
        if qtype not in {"short_text", "text", "essay"}:
            continue

        item_id = str(item.get("id") or "")
        submitted = answers_by_item.get(item_id, {})
        user_answer = str(submitted.get("selected_value") or "").strip()
        reference_answer = str(item.get("answer") or item.get("reference_answer") or "").strip()
        prompt = str(item.get("prompt") or "").strip()

        if not item_id:
            continue

        if not user_answer:
            task_meta.append(("empty", item_id, item, None))
            continue

        tasks.append(
            grade_user_answer(
                question=prompt,
                user_answer=user_answer,
                inference_model_name=reasoning_model_name,
                reference_answer=reference_answer,
                no_max_tokens=1024,
                response_language=response_language,
            )
        )
        task_meta.append(("llm", item_id, item, user_answer))

    results_map: dict[str, dict] = {}

    if tasks:
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
    else:
        task_results = []

    llm_idx = 0
    for mode, item_id, item, user_answer in task_meta:
        if mode == "empty":
            results_map[item_id] = {
                "grade": 5,
                "summary": "No answer submitted.",
            }
        else:
            result = task_results[llm_idx]
            llm_idx += 1

            if isinstance(result, Exception):
                results_map[item_id] = {
                    "grade": 5,
                    "summary": f"Failed to grade this answer: {str(result)}",
                }
            else:
                results_map[item_id] = {
                    "grade": int(result.get("grade", 5)),
                    "summary": result.get("summary", ""),
                }

    return results_map

async def grade_module_quiz(
    course_json: dict,
    module: dict,
    quiz: dict,
    answers: list[dict],
    reasoning_model_name: str | None,
    response_language: str,
) -> dict:
    items = _safe_list(quiz.get("items"))
    answers_by_item = normalize_answers_by_item(answers)
    pass_percent = get_module_quiz_pass_percent(course_json, module, quiz)

    text_results = await grade_text_quiz_items(
        items=items,
        answers_by_item=answers_by_item,
        reasoning_model_name=reasoning_model_name,
        response_language=response_language,
    )

    total_points = 0.0
    score = 0.0
    feedback = []

    for item in items:
        item_id = str(item.get("id") or "")
        qtype = str(item.get("type") or "")
        points = float(item.get("points", 1))
        prompt = str(item.get("prompt") or "")
        total_points += points

        submitted = answers_by_item.get(item_id, {})
        item_feedback = {
            "item_id": item_id,
            "prompt": prompt,
            "type": qtype,
            "awarded_points": 0.0,
            "max_points": points,
            "correct": False,
            "summary": None,
            "grade": None,
        }

        if qtype == "mcq":
            selected_ids = set(submitted.get("selected_choice_ids") or [])
            correct_ids = {
                c.get("id")
                for c in _safe_list(item.get("choices"))
                if c.get("correct") is True
            }
            if selected_ids == correct_ids:
                score += points
                item_feedback["awarded_points"] = points
                item_feedback["correct"] = True

        elif qtype == "multi_select":
            selected_ids = set(submitted.get("selected_choice_ids") or [])
            correct_ids = {
                c.get("id")
                for c in _safe_list(item.get("choices"))
                if c.get("correct") is True
            }
            if selected_ids == correct_ids:
                score += points
                item_feedback["awarded_points"] = points
                item_feedback["correct"] = True

        elif qtype == "true_false":
            selected_value = submitted.get("selected_value")
            if isinstance(selected_value, str):
                selected_bool = selected_value.lower() == "true"
            else:
                selected_bool = bool(selected_value)
            if selected_bool == bool(item.get("answer")):
                score += points
                item_feedback["awarded_points"] = points
                item_feedback["correct"] = True

        elif qtype == "numeric":
            raw_value = submitted.get("selected_value")
            try:
                submitted_num = float(raw_value)
                answer_spec = _safe_dict(item.get("answer"))
                target = float(answer_spec.get("value", 0.0))
                tolerance = float(answer_spec.get("tolerance", 0.0))
                if abs(submitted_num - target) <= tolerance:
                    score += points
                    item_feedback["awarded_points"] = points
                    item_feedback["correct"] = True
            except Exception:
                pass

        elif qtype in {"short_text", "text", "essay"}:
            text_result = _safe_dict(text_results.get(item_id))
            grade = int(text_result.get("grade", 5))
            summary = text_result.get("summary", "")
            ratio = free_text_credit_ratio_from_grade(grade)

            awarded = round(points * ratio, 2)
            score += awarded

            item_feedback["awarded_points"] = awarded
            item_feedback["correct"] = grade in (1, 2)
            item_feedback["summary"] = summary
            item_feedback["grade"] = grade

        else:
            item_feedback["summary"] = f"Unsupported item type '{qtype}'"

        feedback.append(item_feedback)

    percent = 0.0 if total_points == 0 else round((score / total_points) * 100.0, 2)
    passed = percent >= pass_percent
    german_grade = german_grade_from_percent(percent)

    return {
        "score": score,
        "total_points": total_points,
        "percent": percent,
        "passed": passed,
        "pass_percent": pass_percent,
        "german_grade": german_grade,
        "feedback": feedback,
    }

async def submit_module_quiz_attempt_for_learner(
    course_id: int,
    module_id: str,
    assessment_id: str,
    answers: list[dict],
    learner_user_id: int,
    db: AsyncSession,
    response_language: str,
    reasoning_model_name: str | None = None,
) -> dict:
    course = await get_course_with_json(course_id, db)
    course_json = _safe_dict(course.course_json)

    module, quiz = get_module_quiz(course_json, module_id, assessment_id)
    
    graded_result = await grade_quiz(
        course_json=course_json,
        quiz=quiz,
        answers=answers,
        response_language=response_language,
        reasoning_model_name=reasoning_model_name,
        module=module,
    )
    
    progress = await get_or_create_progress(course_id, learner_user_id, db)

    progress_json = _normalize_progress_json(deepcopy(progress.progress_json))
    
    attempt = LearnerQuizAttemptModel(
        course_id=course_id,
        learner_user_id=learner_user_id,
        module_id=module_id,
        assessment_id=assessment_id,
        assessment_type="module_quiz",
        submitted_answers_json=answers or [],
        feedback_json=graded_result["feedback"],
        score=graded_result["score"],
        total_points=graded_result["total_points"],
        percent=graded_result["percent"],
        passed=graded_result["passed"],
        german_grade=graded_result["german_grade"],
    )
    db.add(attempt)
    await db.flush()

    module_status = _safe_dict(progress_json["module_status"].get(module_id))
    previous_best_percent = float(module_status.get("best_percent", 0.0) or 0.0)
    previous_passed = bool(module_status.get("quiz_passed", False))

    current_percent = float(graded_result["percent"])
    current_grade = float(graded_result["german_grade"])

    best_grade = min(float(module_status.get("best_german_grade", current_grade)), current_grade)
    
    progress_json["module_status"][str(module_id)] = {
        "assessment_id": assessment_id,
        "quiz_attempted": True,
        "quiz_passed": previous_passed or bool(graded_result["passed"]),
        "last_percent": current_percent,
        "best_percent": max(previous_best_percent, current_percent),
        "last_german_grade": current_grade,
        "best_german_grade": best_grade,
        "attempt_count": int(module_status.get("attempt_count", 0)) + 1,
        "latest_attempt_id": attempt.attempt_id,
    }

    progress.current_module_id = module_id
    progress_json["course_completion"] = compute_course_completion(course_json, progress_json)
    progress.completion_percent = compute_completion_percent(course_json, progress_json)

    _assign_progress_json(progress, progress_json)
    
    await db.commit()
    await db.refresh(progress)

    snapshot = build_progress_snapshot(progress)
    
    return {
        "message": "submitted",
        "result": {
            "assessment_type": "module_quiz",
            "assessment_id": assessment_id,
            "module_id": module_id,
            "score": graded_result["score"],
            "total_points": graded_result["total_points"],
            "percent": graded_result["percent"],
            "passed": graded_result["passed"],
            "pass_percent": graded_result["pass_percent"],
            "german_grade": graded_result["german_grade"],
            "feedback": graded_result["feedback"],
        },
        "progress_snapshot": snapshot,
        "attempt_summaries": build_attempt_summaries(snapshot),
    }

async def submit_final_quiz_attempt_for_learner(
    course_id: int,
    assessment_id: str,
    answers: list[dict],
    learner_user_id: int,
    db: AsyncSession,
    response_language: str,
    reasoning_model_name: str | None = None,
) -> dict:
    course = await get_course_with_json(course_id, db)
    course_json = _safe_dict(course.course_json)

    progress = await get_or_create_progress(course_id, learner_user_id, db)
    
    progress_json = _normalize_progress_json(deepcopy(progress.progress_json))
    
    allowed, reason = can_attempt_final_quiz(course_json, progress_json)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=reason,
        )

    quiz = get_final_quiz(course_json, assessment_id)
    graded_result = await grade_quiz(
        course_json=course_json,
        quiz=quiz,
        answers=answers,
        response_language=response_language,
        reasoning_model_name=reasoning_model_name,
        module=None,
    )

    attempt = LearnerQuizAttemptModel(
        course_id=course_id,
        learner_user_id=learner_user_id,
        module_id=None,
        assessment_id=assessment_id,
        assessment_type="final_quiz",
        submitted_answers_json=answers or [],
        feedback_json=graded_result["feedback"],
        score=graded_result["score"],
        total_points=graded_result["total_points"],
        percent=graded_result["percent"],
        passed=graded_result["passed"],
        german_grade=graded_result["german_grade"],
    )
    db.add(attempt)
    await db.flush()

    final_status = _safe_dict(progress_json.get("final_status"))
    previous_best_percent = float(final_status.get("best_percent", 0.0) or 0.0)
    current_percent = float(graded_result["percent"])
    current_grade = float(graded_result["german_grade"])
    best_grade = min(float(final_status.get("best_german_grade", current_grade)), current_grade)

    progress_json["final_status"] = {
        "assessment_id": assessment_id,
        "attempted": True,
        "passed": bool(graded_result["passed"]),
        "last_percent": current_percent,
        "best_percent": max(previous_best_percent, current_percent),
        "last_german_grade": current_grade,
        "best_german_grade": best_grade,
        "attempt_count": int(final_status.get("attempt_count", 0)) + 1,
        "latest_attempt_id": attempt.attempt_id,
    }

    progress.current_nav = "final_quiz"
    progress.current_module_id = None
    
    progress_json["course_completion"] = compute_course_completion(course_json, progress_json)
    
    progress.completion_percent = compute_completion_percent(course_json, progress_json)

    _assign_progress_json(progress, progress_json)
    
    await db.commit()
    await db.refresh(progress)

    snapshot = build_progress_snapshot(progress)

    return {
        "message": "submitted",
        "result": {
            "assessment_type": "final_quiz",
            "assessment_id": assessment_id,
            "module_id": None,
            "score": graded_result["score"],
            "total_points": graded_result["total_points"],
            "percent": graded_result["percent"],
            "passed": graded_result["passed"],
            "pass_percent": graded_result["pass_percent"],
            "german_grade": graded_result["german_grade"],
            "feedback": graded_result["feedback"],
        },
        "progress_snapshot": snapshot,
        "attempt_summaries": build_attempt_summaries(snapshot),
    }
