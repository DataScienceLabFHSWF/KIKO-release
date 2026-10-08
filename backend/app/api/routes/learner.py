# backend/app/api/routes/learner.py

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Body, Path
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import PlainTextResponse
from pathlib import Path as PathlibPath
from app.schemas import (
    LearnerStatistics, LearnerSubmitQuizRequest, LearnerProgressUpdateRequest,
    COMMON_ERROR_RESPONSES, LearnerAvailableCourseResponse, LearnerCourseDetailsResponse,
    LearnerCourseSummaryResponse, LearnerDashboardResponse, LearnerProgressSaveResponse,
    LearnerProgressUpdateRequest, LearnerQuizSubmitResponse, LearnerRecommendedCourseResponse,
    LearnerStatistics, LearnerSubmitQuizRequest
)
from app.database import get_db
from app.services import (
    get_learner_statistics, require_role, list_enrolled_courses,
    list_recommended_courses, enroll_user_in_course, unenroll_user_from_course,
    dismiss_recommendation, get_user_profile_by_email, fetch_course_details,
    list_all_courses_excluding_enrolled, submit_module_quiz_attempt_for_learner, update_progress_snapshot,
    get_request_lang, submit_final_quiz_attempt_for_learner, require_active_course_enrollment, get_app_config_and_libary_available
)

logger = logging.getLogger(__name__)

router = APIRouter(responses=COMMON_ERROR_RESPONSES)

async def _get_current_learner_profile(
    user: dict, 
    db: AsyncSession
):
    """Helper function to fetch the current learner's profile from the database."""
    
    profile = await get_user_profile_by_email(user["email"], db)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="❌ User not found",
        )

    return profile

# STATIC route FIRST
@router.get(
    "/dashboard", 
    response_model=LearnerDashboardResponse,
    operation_id="get_learner_dashboard"
)
async def get_learner_dashboard(
    user=Depends(require_role(["Learner"]))
) -> LearnerDashboardResponse:
    """Learner dashboard with course management and statistics."""
    logger.info(f"ℹ️ Accessing learner dashboard for user: {user['email']}")
    return LearnerDashboardResponse(
        message=f"Welcome Learner: {user['email']}"
    )

@router.get(
    "/statistics", 
    response_model=LearnerStatistics,
    operation_id="get_learner_statistics"
)
async def get_learner_stats(
    user= Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db)
) -> LearnerStatistics:
    """Get statistics for the learner dashboard."""
    logger.info(f"ℹ️ Fetching learner statistics for user: {user['email']}")
    try:
        logger.info(f"✅ Successfully fetched learner statistics for user: {user['email']}")
        return await get_learner_statistics(user["email"], db)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ Error fetching learner statistics")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Error fetching learner statistics: {str(e)}"
        )

@router.get(
    "/courses/enrolled", 
    response_model=list[LearnerCourseSummaryResponse],
    operation_id="list_enrolled_courses"
)
async def get_enrolled(
    user=Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db),
) -> list[LearnerCourseSummaryResponse]:
    """Get list of courses the learner is enrolled in."""
    try:
        logger.info(f"ℹ️ Fetching enrolled courses for user: {user['email']}")

        profile = await _get_current_learner_profile(user, db)
        
        list_courses = await list_enrolled_courses(profile.user_id, db)

        logger.info(f"✅ Successfully fetched enrolled courses for user: {user['email']}, courses count: {len(list_courses)}")

        response = [
            LearnerCourseSummaryResponse.model_validate(course)
            for course in list_courses
        ]

        logger.info(f"✅ Returning response for enrolled courses: {response} for user: {user['email']}")

        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ Error fetching enrolled courses")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"❌ Error fetching enrolled courses: {str(e)}"
        ) from e

@router.get(
    "/courses/recommended",
    response_model=list[LearnerRecommendedCourseResponse],
    operation_id="list_recommended_courses"
)
async def get_recommended(
    user=Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db),
) -> list[LearnerRecommendedCourseResponse]:
    """Get list of recommended courses for the learner."""
    try:
        logger.info(f"ℹ️ Fetching recommended courses for user: {user['email']}")

        profile = await _get_current_learner_profile(user, db)
        
        recommended_courses = await list_recommended_courses(profile.user_id, db)

        logger.info(f"✅ Successfully fetched recommended courses for user: {user['email']}, courses count: {len(recommended_courses)}")
        
        return [
            LearnerRecommendedCourseResponse.model_validate(course)
            for course in recommended_courses
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ Error fetching recommended courses")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Error fetching recommended courses: {str(e)}"
        ) from e

@router.get(
    "/courses/all",
    response_model=list[LearnerAvailableCourseResponse],
    operation_id="list_available_courses"
)
async def all_courses(
    user = Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db),
) -> list[LearnerAvailableCourseResponse]:
    """Get list of all courses excluding enrolled ones for the learner."""
    try:
        logger.info(f"ℹ️ Fetching all available courses for user: {user['email']}")
        
        profile = await _get_current_learner_profile(user, db)
        
        courses = await list_all_courses_excluding_enrolled(profile.user_id, db)
        
        logger.info(f"✅ Successfully fetched all available courses for user: {user['email']}, courses count: {len(courses)}")
        
        return [
            LearnerAvailableCourseResponse.model_validate(course)
            for course in courses
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ Error fetching available courses")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Error fetching available courses: {str(e)}"
        ) from e

# PARAM route AFTER
@router.post(
    "/courses/{course_id}/enroll", 
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="enroll_in_course"
)
async def post_enroll(
    course_id: int,
    user=Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Enroll the learner in a specified course."""
    try:
        logger.info(f"ℹ️ Enrolling user: {user['email']} in course_id: {course_id}")

        profile = await _get_current_learner_profile(user, db)
        
        await enroll_user_in_course(profile.user_id, course_id, db)

        logger.info(f"✅ Successfully enrolled user: {user['email']} in course_id: {course_id}")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ Error enrolling Learner in course")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Error enrolling user in course: {str(e)}"
        ) from e

@router.delete(
    "/courses/{course_id}/enrollment", 
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="unenroll_from_course"
)
async def delete_enrollment(
    course_id: int,
    user=Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Unenroll the learner from a specified course."""
    try:
        logger.info(f"ℹ️ Unenrolling user: {user['email']} from course_id: {course_id}")

        profile = await _get_current_learner_profile(user, db)
        
        await unenroll_user_from_course(profile.user_id, course_id, db)

        logger.info(f"✅ Successfully unenrolled user: {user['email']} from course_id: {course_id}")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ Error unenrolling Learner from course")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Error unenrolling user from course: {str(e)}"
        ) from e

@router.delete(
    "/courses/recommended/{course_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="dismiss_recommended_course"
)
async def delete_recommended(
    course_id: int,
    user=Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Dismiss a recommended course for the learner."""
    try:
        logger.info(f"ℹ️ Dismissing recommended course_id: {course_id} for user: {user['email']}")

        profile = await _get_current_learner_profile(user, db)
        
        await dismiss_recommendation(profile.user_id, course_id, db)

        logger.info(f"✅ Successfully dismissed recommended course_id: {course_id} for user: {user['email']}")
        
        return None
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get(
    "/courses/{course_id}", 
    response_model=LearnerCourseDetailsResponse,
    operation_id="get_learner_course_details"
)
async def course_details(
    course_id: int,
    user = Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db),
) -> LearnerCourseDetailsResponse:
    """Get detailed information about a specific course for the learner.""" 
    try:
        logger.info(f"ℹ️ Fetching course details for course_id: {course_id} and user: {user['email']}")
        
        # Resolve learner profile
        user_profile = await _get_current_learner_profile(user, db)
        
        course = await fetch_course_details(user_profile.user_id, course_id, db)
        
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ Course not found")
        
        logger.info(f"✅ Successfully fetched course details for course_id: {course_id} and user: {user['email']}")
        
        return LearnerCourseDetailsResponse.model_validate(course)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error fetching course details for course_id: {course_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error while loading course details: {str(e)}",
        ) from e

@router.get(
    "/course-template/md", 
    response_class=PlainTextResponse,
    operation_id="get_course_template_markdown",
    responses={
        200: {
            "content": {"text/plain": {"schema": {"type": "string"}}},
            "description": "Course template markdown",
        },
        **COMMON_ERROR_RESPONSES,
    },
)
def get_course_template_md(
    user = Depends(require_role(["Learner"]))
) -> str:
    """Endpoint to retrieve the course template in markdown format."""

    try:
        logger.info(f"ℹ️ Fetching course template markdown for user: {user['email']}")
        
        md_path = PathlibPath("/backend/data/EducTUM/") / "kiko-course-template.md"
        
        logger.info(f"ℹ️ Looking for template at: {md_path}")
        
        if not md_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Template not found: {md_path}")
        
        logger.info(f"✅ Found template at: {md_path}")
        return md_path.read_text(encoding="utf-8")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error reading template: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"❌ Error reading template: {str(e)}")

@router.post(
    "/courses/{course_id}/module-quizzes/{module_id}/submit", 
    response_model=LearnerQuizSubmitResponse,
    operation_id="submit_module_quiz_attempt"
)
async def create_quiz_attempt(
    course_id: int = Path(..., gt=0),
    module_id: str = Path(...),
    payload: LearnerSubmitQuizRequest = Body(...),
    user=Depends(require_role(["Learner"])),
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db),
) -> LearnerQuizSubmitResponse:
    """
    Submit a learner's module quiz attempt, grade it, persist it, and update course progress.
    """
    try:
        logger.info(f"ℹ️ Submitting quiz attempt for course_id: {course_id}, module_id: {module_id} by user: {user['email']}")
        
        user_profile = await _get_current_learner_profile(user, db)
        
        await require_active_course_enrollment(
            course_id=course_id,
            user_id=user_profile.user_id,
            db=db,
        )
        
        configs = await get_app_config_and_libary_available(db=db)
        
        if not configs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ Application configurations not found")
        
        default_reasoning_model_name = payload.reasoning_model_name or configs.get("app_config").default_reasoning_model
        
        result = await submit_module_quiz_attempt_for_learner(
            course_id=course_id,
            module_id=module_id,
            assessment_id=payload.assessment_id,
            answers=[item.model_dump() for item in payload.answers],
            learner_user_id=user_profile.user_id,
            db=db,
            response_language=response_language,
            reasoning_model_name=default_reasoning_model_name,
        )

        logger.info(f"✅ Successfully submitted the module id: {module_id}, quiz: {result} by user: {user_profile.user_id}")

        response = LearnerQuizSubmitResponse.model_validate(result)

        logger.info(f"✅ Returning response for module quiz submission: {response} for course_id: {course_id}, module_id: {module_id}, user_id: {user_profile.user_id}")
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Failed to submit module quiz for course_id: {course_id}, module_id: {module_id}, user_id: {user_profile.user_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ module_quiz_submit_failed: {str(e)}",
        ) from e

@router.post(
    "/courses/{course_id}/final-quiz/submit",
    response_model=LearnerQuizSubmitResponse,
    operation_id="submit_final_quiz_attempt"
)
async def submit_final_quiz(
    course_id: int = Path(..., gt=0),
    payload: LearnerSubmitQuizRequest = Body(...),
    user=Depends(require_role(["Learner"])),
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db),
) -> LearnerQuizSubmitResponse:
    """Submit a learner's final quiz attempt for the course, grade it, persist it, and update course progress."""
    
    try:
        logger.info(f"ℹ️ Submitting final quiz attempt for course_id: {course_id} by user: {user['email']}")

        user_profile = await _get_current_learner_profile(user, db)
        
        await require_active_course_enrollment(
            course_id=course_id,
            user_id=user_profile.user_id,
            db=db,
        )

        configs = await get_app_config_and_libary_available(db=db)
        
        if not configs:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ Application configurations not found")
        
        default_reasoning_model_name = payload.reasoning_model_name or configs.get("app_config").default_reasoning_model

        result = await submit_final_quiz_attempt_for_learner(
            course_id=course_id,
            assessment_id=payload.assessment_id,
            answers=[item.model_dump() for item in payload.answers],
            learner_user_id=user_profile.user_id,
            db=db,
            response_language=response_language,
            reasoning_model_name=default_reasoning_model_name,
        )
        
        logger.info(f"✅ Successfully submitted the Final quiz: {result} by user: {user_profile.user_id}")

        return LearnerQuizSubmitResponse.model_validate(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Failed to submit final quiz for course_id: {course_id}, user_id: {user_profile.user_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ final_quiz_submit_failed: {str(e)}",
        ) from e

@router.put(
    "/courses/{course_id}/progress",
    response_model=LearnerProgressSaveResponse,
    operation_id="save_learner_course_progress"
)
async def save_progress(
    course_id: int = Path(..., gt=0),
    payload: LearnerProgressUpdateRequest = Body(...),
    user=Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db),
) -> LearnerProgressSaveResponse:
    """Save the learner's current progress in the course, including navigation state and practice quiz answers."""
    
    try:
        logger.info(f"ℹ️ Saving progress for course_id: {course_id} by user: {user['email']} with payload: {payload}")
        
        user_profile = await _get_current_learner_profile(user, db)
        
        await require_active_course_enrollment(
            course_id=course_id,
            user_id=user_profile.user_id,
            db=db,
        )
        
        snapshot = await update_progress_snapshot(
            course_id=course_id,
            learner_user_id=user_profile.user_id,
            current_nav=payload.current_nav,
            current_module_id=payload.current_module_id,
            practice_answers=payload.practice_answers,
            db=db,
        )
        
        logger.info(f"✅ Successfully saved progress snapshot for course_id: {course_id}, user_id: {user_profile.user_id}, snapshot: {snapshot}")
        
        return LearnerProgressSaveResponse(
            message="Progress saved",
            progress_snapshot=snapshot,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Failed to save progress for course_id: {course_id}, user_id: {user_profile.user_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Failed to save learner progress: {str(e)}",
        ) from e
