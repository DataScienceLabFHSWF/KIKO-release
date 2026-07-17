# backend/app/services/learner_service.py
import logging, yaml
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, insert, delete
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from app.models import (
    LearnerCourseProgressModel, ExamSubmissionModel, CourseModel,
    RecommendedCourseModel, ChatHistoryModel
)
from .user_service import get_user_profile_by_email, get_system_user_id
from .learner_course_progress_service import (build_attempt_summaries, build_progress_snapshot)

logger = logging.getLogger(__name__)

# Template course titles used to identify instructor clones
TEMPLATE_TITLES = [
    "The World of Birds: Adaptations for Flight",
    "Introduction to Climate Change: The Science of Warming",
    "Small Modular Reactors (SMRs) Explained",
    "Nuclear Fusion: The Energy of the Future"
]

def _safe_dict(value: Any) -> dict:
    return value if isinstance(value, dict) else {}

def _default_course_completion() -> dict:
    return {
        "status": "not_enrolled",
        "eligible_for_final_quiz": False,
        "completed": False,
        "weighted_percent": None,
        "german_grade": None,
    }

def _default_progress_snapshot() -> dict:
    return {
        "current_nav": "overview",
        "current_module_id": None,
        "completion_percent": 0.0,
        "module_status": {},
        "final_status": {},
        "practice_answers": {},
        "course_completion": _default_course_completion(),
    }

def _progress_meta(progress: LearnerCourseProgressModel | None) -> dict:
    
    if not progress:
        return _default_course_completion()

    progress_json = _safe_dict(progress.progress_json)
    course_completion = _safe_dict(progress_json.get("course_completion"))

    completed = bool(course_completion.get("completed")) or float(progress.completion_percent or 0.0) >= 100.0
    status_value = course_completion.get("status") or ("completed" if completed else "in_progress")

    return {
        "status": status_value,
        "eligible_for_final_quiz": bool(course_completion.get("eligible_for_final_quiz", False)),
        "completed": completed,
        "weighted_percent": course_completion.get("weighted_percent"),
        "german_grade": course_completion.get("german_grade"),
    }

def _initial_progress_json() -> dict:
    return {
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
    }

async def get_learner_statistics(
    email: str, 
    db: AsyncSession
) -> dict:
    try:
        # Fetch user by email
        user = await get_user_profile_by_email(email, db)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="❌ User not found",
            )
        
        user_id = user.user_id

        total_enrolled_q = await db.execute(
            select(func.count())
            .select_from(LearnerCourseProgressModel)
            .where(LearnerCourseProgressModel.learner_user_id == user_id)
        )
        
        total_completed_q = await db.execute(
            select(func.count())
            .select_from(LearnerCourseProgressModel)
            .where(
                LearnerCourseProgressModel.learner_user_id == user_id,
                LearnerCourseProgressModel.completion_percent >= 100.0,
            )
        )
        
        passed_q = await db.execute(
            select(func.count())
            .select_from(ExamSubmissionModel)
            .where(
                ExamSubmissionModel.user_id == user_id,
                ExamSubmissionModel.passed == 1,
            )
        )
        
        failed_q = await db.execute(
            select(func.count())
            .select_from(ExamSubmissionModel)
            .where(
                ExamSubmissionModel.user_id == user_id,
                ExamSubmissionModel.passed == 0,
            )
        )
        
        inprogress_q = await db.execute(
            select(func.count())
            .select_from(ExamSubmissionModel)
            .where(
                ExamSubmissionModel.user_id == user_id,
                ExamSubmissionModel.passed.is_(None),
            )
        )
        
        questions_q = await db.execute(
            select(func.count())
            .select_from(ChatHistoryModel)
            .where(ChatHistoryModel.user_id == user_id)
        )
        
        latest_progress_q = await db.execute(
            select(func.max(LearnerCourseProgressModel.updated_at))
            .where(LearnerCourseProgressModel.learner_user_id == user_id)
        )

        total_enrolled = total_enrolled_q.scalar() or 0
        total_completed = total_completed_q.scalar() or 0
        in_progress = max(total_enrolled - total_completed, 0)
        progress_percent = int((in_progress / total_enrolled) * 100) if total_enrolled else 0

        latest_progress_at = latest_progress_q.scalar()
        last_activity = latest_progress_at or user.last_login or datetime.now(timezone.utc)

        return {
            "courses_enroll": total_enrolled,
            "courses_completed": total_completed,
            "courses_inprogress": in_progress,
            "courses_progress_percent": progress_percent,
            "exams_passed": passed_q.scalar() or 0,
            "exams_failed": failed_q.scalar() or 0,
            "exams_inprogress": inprogress_q.scalar() or 0,
            "questions_asked": questions_q.scalar() or 0,
            "last_activity": last_activity.isoformat(),
        }
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during get learner statistics: {str(e)}",
        ) from e

async def list_enrolled_courses(
    user_id: int, 
    db: AsyncSession
) -> List[Dict]:
    try:
        stmt = (
            select(CourseModel, LearnerCourseProgressModel)
            .join(
                LearnerCourseProgressModel,
                LearnerCourseProgressModel.course_id == CourseModel.course_id,
            )
            .where(LearnerCourseProgressModel.learner_user_id == user_id)
            .order_by(LearnerCourseProgressModel.updated_at.desc())
        )

        result = await db.execute(stmt)
        rows = result.all()

        payload: list[dict] = []
        for course, progress in rows:
            meta = _progress_meta(progress)
            
            payload.append(
                {
                    "course_id": course.course_id,
                    "title": course.title,
                    "summary": course.summary,
                    "completion_percent": float(progress.completion_percent or 0.0),
                    "status": meta["status"],
                    "completed": meta["completed"],
                    "eligible_for_final_quiz": meta["eligible_for_final_quiz"],
                    "weighted_percent": meta["weighted_percent"],
                    "german_grade": meta["german_grade"],
                    "updated_at": progress.updated_at.isoformat() if progress.updated_at else None,
                }
            )

        return payload
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during get learner enrolled courses: {str(e)}",
        ) from e

async def list_recommended_courses(
    user_id: int,
    db: AsyncSession
) -> List[Dict]:
    """List recommended courses for the learner, with reason and score.
    Shows: system templates + instructor original courses (no clones)."""

    try:
        # Get system user ID
        system_user_id = await get_system_user_id(db)
        
        if not system_user_id:
            # Fallback: if no system user, show all recommended courses
            stmt = (
                select(RecommendedCourseModel, CourseModel)
                .join(CourseModel, CourseModel.course_id == RecommendedCourseModel.course_id)
                .where(RecommendedCourseModel.user_id == user_id)
                .order_by(RecommendedCourseModel.score.desc())
            )
        else:
            # Show templates + instructor originals (exclude clones by title)
            stmt = (
                select(RecommendedCourseModel, CourseModel)
                .join(CourseModel, CourseModel.course_id == RecommendedCourseModel.course_id)
                .where(
                    RecommendedCourseModel.user_id == user_id,
                    (CourseModel.is_template == True) | 
                    ((CourseModel.created_by != system_user_id) & 
                     (CourseModel.title.notin_(TEMPLATE_TITLES)))
                )
                .order_by(RecommendedCourseModel.score.desc())
            )
        
        result = await db.execute(stmt)
        
        rows = result.all()
        
        return [
            {
                "course_id": course.course_id,
                "title": course.title,
                "summary": course.summary,
                "reason": recommendation.reason,
                "score": recommendation.score,
            }
            for recommendation, course in rows
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during get learner recommended courses: {str(e)}",
        ) from e

async def enroll_user_in_course(
    user_id: int, 
    course_id: int, 
    db: AsyncSession
) -> None:
    try:
        # no-dup enrollment
        existing = await get_course_progress(user_id=user_id, course_id=course_id, db=db)

        if existing is None:
            db.add(
                LearnerCourseProgressModel(
                    learner_user_id=user_id,
                    course_id=course_id,
                    current_nav="overview",
                    current_module_id=None,
                    completion_percent=0.0,
                    progress_json=_initial_progress_json(),
                )
            )

        await db.execute(
            delete(RecommendedCourseModel)
            .where(
                RecommendedCourseModel.user_id == user_id,
                RecommendedCourseModel.course_id == course_id,
            )
        )

        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error: {str(e)}",
        ) from e
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during enrolling the user in courses: {str(e)}",
        ) from e

async def unenroll_user_from_course(
    user_id: int, 
    course_id: int, 
    db: AsyncSession
) -> None:
    try:
        await db.execute(
            delete(LearnerCourseProgressModel)
            .where(
                LearnerCourseProgressModel.learner_user_id == user_id,
                LearnerCourseProgressModel.course_id == course_id,
            )
        )
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error: {str(e)}",
        ) from e
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during un-enrolling the user from courses: {str(e)}",
        ) from e

async def dismiss_recommendation(
    user_id: int, 
    course_id: int, 
    db: AsyncSession
) -> None:
    
    try:
        await db.execute(
            delete(RecommendedCourseModel)
            .where(
                RecommendedCourseModel.user_id == user_id,
                RecommendedCourseModel.course_id == course_id
            )
        )

        await db.commit()

        return {"ok": True}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error: {str(e)}",
        ) from e
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during dismissing recommendation: {str(e)}",
        ) from e

async def get_course(
    course_id: int, 
    db: AsyncSession
) -> Optional[CourseModel]:
    """
    Load a course with its questions and quizzes.
    """
    try:
        result = await db.execute(
            select(CourseModel)
            .options(joinedload(CourseModel.questions))
            .options(joinedload(CourseModel.quiz))
            .where(CourseModel.course_id == course_id)
        )
        return result.scalars().first()
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
            detail=f"❌ Unexpected error during getting course with questions: {str(e)}"
        )

async def get_course_progress(
    user_id: int,
    course_id: int,
    db: AsyncSession,
) -> Optional[LearnerCourseProgressModel]:
    try:
        result = await db.execute(
            select(LearnerCourseProgressModel)
            .where(
                LearnerCourseProgressModel.learner_user_id == user_id,
                LearnerCourseProgressModel.course_id == course_id,
            )
        )
        
        return result.scalars().first()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error: {str(e)}",
        ) from e

async def get_user_enrollment(
    user_id: int, 
    course_id: int, 
    db: AsyncSession
) -> Optional[LearnerCourseProgressModel]:
    """
    Return the learner's enrollment for a given course (if any).
    """
    try:
        res = await db.execute(
            select(LearnerCourseProgressModel)
            .where(LearnerCourseProgressModel.learner_user_id == user_id, LearnerCourseProgressModel.course_id == course_id,)
        )
        
        return res.scalars().first()
    except SQLAlchemyError as e:        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error: {str(e)}"
        )
    except Exception as e:        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during dismissing the user from recommendation: {str(e)}"
        )

def build_fallback_course_json(course: Any) -> Dict[str, Any]:
    """
    Fallback for older courses that do not yet have course_json/template_markdown stored.
    This keeps the learner page from breaking.
    """
    fallback_title = getattr(course, "title", "Untitled course")
    fallback_summary = getattr(course, "summary", "") or ""

    final_quiz = {}
    quiz_obj = getattr(course, "quiz", None)
    if quiz_obj is not None and getattr(quiz_obj, "content", None):
        try:
            parsed_quiz = yaml.safe_load(quiz_obj.content) or {}
            if isinstance(parsed_quiz, dict):
                final_quiz = parsed_quiz
        except Exception:
            final_quiz = {}

    return {
        "schema": "course.v1-fallback",
        "course": {
            "id": f"course-{getattr(course, 'course_id', 'unknown')}",
            "title": fallback_title,
            "provider": None,
            "language": None,
            "level": None,
            "tags": [],
            "estimated_minutes": None,
            "prerequisites": [],
        },
        "instructors": [],
        "grading": {
            "pass_percent": 70,
            "assessment_weights": {},
            "policy": {},
        },
        "resources": [],
        "overview_md": fallback_summary,
        "modules": [],
        "final_quiz": final_quiz,
    }

async def fetch_course_details(
    user_id: int, 
    course_id: int, 
    db: AsyncSession
) -> Dict[str, Any]:
    try:
        course = await get_course(course_id, db)
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="❌ Course not found",
            )

        progress = await get_course_progress(user_id=user_id, course_id=course_id, db=db)
        meta = _progress_meta(progress)

        snapshot = build_progress_snapshot(progress) if progress else _default_progress_snapshot()
        attempt_summaries = build_attempt_summaries(progress.progress_json or {}) if progress else {
            "module_quizzes": {},
            "final_quiz": {},
            "course_completion": _default_course_completion(),
        }

        return {
            "course": {
                "course_id": course.course_id,
                "title": course.title,
                "summary": course.summary,
                "created_at": course.created_at.isoformat() if course.created_at else None,
            },
            "enrollment": {
                "is_enrolled": progress is not None,
                "enrolled": progress is not None,
                "status": "enrolled" if progress else "not_enrolled",
                "completion_percent": float(progress.completion_percent or 0.0) if progress else 0.0,
                "completed": meta["completed"],
            },
            "course_json": course.course_json or {},
            "template_markdown": course.template_markdown or "",
            "progress_snapshot": snapshot,
            "attempt_summaries": attempt_summaries,
        }
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during fetching course details: {str(e)}",
        ) from e

async def list_all_courses_excluding_enrolled(
    user_id: int, 
    db: AsyncSession
):
    try:
        system_user_id = await get_system_user_id(db)

        enrolled_subquery = select(LearnerCourseProgressModel.course_id).where(
            LearnerCourseProgressModel.learner_user_id == user_id
        )

        if not system_user_id:
            stmt = (
                select(CourseModel)
                .where(CourseModel.course_id.notin_(enrolled_subquery))
                .order_by(CourseModel.created_at.desc())
            )
        else:
            stmt = (
                select(CourseModel)
                .where(
                    CourseModel.course_id.notin_(enrolled_subquery),
                    (CourseModel.is_template.is_(True))
                    | (
                        (CourseModel.created_by != system_user_id)
                        & (CourseModel.title.notin_(TEMPLATE_TITLES))
                    ),
                )
                .order_by(CourseModel.created_at.desc())
            )

        result = await db.execute(stmt)
        courses = result.scalars().all()

        return [
            {
                "course_id": course.course_id,
                "title": course.title,
                "summary": course.summary,
            }
            for course in courses
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during fetching all courses: {str(e)}",
        ) from e

async def get_course_template_for_learner(
    course_id: int,
    learner_user_id: int,
    db: AsyncSession,
):
    """Fetch the course template for a given course ID, only if it's a system template."""
    try:
        result = await db.execute(
            select(CourseModel)
            .where(
                CourseModel.course_id == course_id,
                CourseModel.is_published.is_(True),
            )
        )
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error: {str(e)}"
        )
    except Exception as e:      
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during fetching templates for learner: {str(e)}"
        )

async def require_active_course_enrollment(
    course_id: int,
    user_id: int,
    db: AsyncSession,
):
    progress = await get_course_progress(user_id=user_id, course_id=course_id, db=db)
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="❌ You must be enrolled in this course to access learner progress and quizzes.",
        )

    return progress
