# backend/app/api/routes/learner.py
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Body, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List
from fastapi.responses import PlainTextResponse
from pathlib import Path as PathlibPath
from app.schemas import LearnerStatistics, LearnerSubmitQuizRequest, LearnerProgressUpdateRequest
from app.database import get_db
from app.services import (
    get_learner_statistics, require_role, list_enrolled_courses,
    list_recommended_courses, enroll_user_in_course, unenroll_user_from_course,
    dismiss_recommendation, get_user_profile_by_email, fetch_course_details,
    list_all_courses_excluding_enrolled, submit_module_quiz_attempt_for_learner, update_progress_snapshot,
    get_request_lang, submit_final_quiz_attempt_for_learner, require_active_course_enrollment
)

logger = logging.getLogger(__name__)

router = APIRouter()

# STATIC route FIRST
@router.get("/dashboard")
async def get_learner_dashboard(
    user=Depends(require_role(["Learner"]))
):
    """Learner dashboard with course management and statistics."""
    return {"message": f"Welcome Learner: {user}"}

@router.get("/statistics", response_model=LearnerStatistics)
async def get_learner_stats(
    user= Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for the learner dashboard."""
    try:
        return await get_learner_statistics(user["email"], db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching learner statistics: {str(e)}"
        )

@router.get("/courses/enrolled", response_model=List[Dict])
async def get_enrolled(
    user=Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db),
):
    """Get list of courses the learner is enrolled in."""
    try:
        profile = await get_user_profile_by_email(user["email"], db)
        
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")
        
        list_courses = await list_enrolled_courses(profile.user_id, db)

        print(f"✅ Enrolled courses: {list_courses} by user :{profile.user_id}")
        
        return list_courses
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/courses/recommended", response_model=List[Dict])
async def get_recommended(
    user=Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db),
):
    """Get list of recommended courses for the learner."""
    try:
        profile = await get_user_profile_by_email(user["email"], db)
        
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")
        
        recc_corses = await list_recommended_courses(profile.user_id, db)
        
        return recc_corses
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/courses/all", response_model=List[Dict])
async def all_courses(
    user = Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db),
):
    """Get list of all courses excluding enrolled ones for the learner."""
    try:
        profile = await get_user_profile_by_email(user["email"], db)
        
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")
        
        response = await list_all_courses_excluding_enrolled(profile.user_id, db)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# PARAM route AFTER
@router.post("/courses/{course_id}/enroll", status_code=status.HTTP_204_NO_CONTENT)
async def post_enroll(
    course_id: int,
    user=Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db),
):
    """Enroll the learner in a specified course."""
    try:
        profile = await get_user_profile_by_email(user["email"], db)
        
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")
        
        response = await enroll_user_in_course(profile.user_id, course_id, db)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/courses/{course_id}/enrollment", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(
    course_id: int,
    user=Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db),
):
    """Unenroll the learner from a specified course."""
    try:
        profile = await get_user_profile_by_email(user["email"], db)
        
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")
        
        response = await unenroll_user_from_course(profile.user_id, course_id, db)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/courses/recommended/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recommended(
    course_id: int,
    user=Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db),
):
    """Dismiss a recommended course for the learner."""
    try:
        profile = await get_user_profile_by_email(user["email"], db)
        
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")
        
        response = await dismiss_recommendation(profile.user_id, course_id, db)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/courses/{course_id}")
async def course_details(
    course_id: int,
    user = Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific course for the learner.""" 
    try:
        # Resolve learner profile
        user_profile = await get_user_profile_by_email(user["email"], db)
        
        if not user_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")
        
        response = await fetch_course_details(user_profile.user_id, course_id, db)
        
        if not response:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ Course not found")
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error while loading course details: {str(e)}",
        ) from e

@router.get("/course-template/md", response_class=PlainTextResponse)
def get_course_template_md(
    user = Depends(require_role(["Learner"]))
):
    try:
        md_path = PathlibPath("/backend/data/EducTUM/") / "kiko-course-template.md"
        print(f"ℹ️ Looking for template at: {md_path}")

        if not md_path.exists():
            raise HTTPException(status_code=404, detail=f"Template not found: {md_path}")

        return md_path.read_text(encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading template: {str(e)}")

@router.post("/courses/{course_id}/module-quizzes/{module_id}/submit")
async def create_quiz_attempt(
    course_id: int = Path(..., gt=0),
    module_id: str = Path(...),
    payload: LearnerSubmitQuizRequest = Body(...),
    user=Depends(require_role(["Learner"])),
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db),
):
    """
    Submit a learner's module quiz attempt, grade it, persist it, and update course progress.
    """
    try:
        user_profile = await get_user_profile_by_email(user["email"], db)
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="❌ User not found",
            )
        
        await require_active_course_enrollment(
            course_id=course_id,
            user_id=user_profile.user_id,
            db=db,
        )
        
        response = await submit_module_quiz_attempt_for_learner(
            course_id=course_id,
            module_id=module_id,
            assessment_id=payload.assessment_id,
            answers=[item.model_dump() for item in payload.answers],
            learner_user_id=user_profile.user_id,
            db=db,
            response_language=response_language,
            reasoning_model_name=payload.reasoning_model_name,
        )

        print(f"✅ Successfully submitted the module id: {module_id}, quiz: {response} by user: {user_profile.user_id}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ module_quiz_submit_failed: {str(e)}",
        ) from e

@router.post("/courses/{course_id}/final-quiz/submit")
async def submit_final_quiz(
    course_id: int = Path(..., gt=0),
    payload: LearnerSubmitQuizRequest = Body(...),
    user=Depends(require_role(["Learner"])),
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db),
):
    try:
        user_profile = await get_user_profile_by_email(user["email"], db)
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="❌ User not found"
            )
        
        await require_active_course_enrollment(
            course_id=course_id,
            user_id=user_profile.user_id,
            db=db,
        )

        response = await submit_final_quiz_attempt_for_learner(
            course_id=course_id,
            assessment_id=payload.assessment_id,
            answers=[item.model_dump() for item in payload.answers],
            learner_user_id=user_profile.user_id,
            db=db,
            response_language=response_language,
            reasoning_model_name=payload.reasoning_model_name,
        )
        
        print(f"✅ Successfully submitted the Final quiz: {response} by user: {user_profile.user_id}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ final_quiz_submit_failed: {str(e)}",
        ) from e

@router.put("/courses/{course_id}/progress")
async def save_progress(
    course_id: int = Path(..., gt=0),
    payload: LearnerProgressUpdateRequest = Body(...),
    user=Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db),
):
    try:
        user_profile = await get_user_profile_by_email(user["email"], db)
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="❌ User not found"
            )
        
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
        
        response = {
            "message": "Progress saved", 
            "progress_snapshot": snapshot
        }
        print(f"✅ Successfully updated the course progress: {response}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Failed to save learner progress: {str(e)}",
        ) from e
