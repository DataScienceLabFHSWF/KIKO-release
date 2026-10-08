# backend/app/api/routes/knowledge_assessment.py

import logging
from fastapi import APIRouter, HTTPException, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import (
    require_role, get_assessment_quiz_for_user, submit_assessment_quiz_for_user,
    get_user_profile_by_email, list_all_questions, fetch_config,
    update_config, remove_question, get_request_lang
)
from app.schemas import (
    AssessmentQuestion, AssessmentPayload, AssessmentResult,
    COMMON_ERROR_RESPONSES, AssessmentAdminQuestionResponse, AssessmentConfigResponse,
    AssessmentConfigUpdateRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(responses=COMMON_ERROR_RESPONSES)

async def _get_current_user_profile(user: dict, db: AsyncSession):
    user_profile = await get_user_profile_by_email(user["email"], db)

    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return user_profile

@router.get(
    "/assessment_quiz", 
    response_model=list[AssessmentQuestion],
    operation_id="get_assessment_quiz"
)
async def get_assessment_quiz(
    user=Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db)
) -> list[AssessmentQuestion]:
    """Fetch the assessment quiz for the authenticated user."""
    try:
        logger.info(f"ℹ️ Fetching assessment quiz for user: {user['email']}")

        data = await get_assessment_quiz_for_user(db=db)

        logger.info(f"✅ Successfully fetched assessment quiz for user: {user['email']} with {len(data)} questions")

        return [
            AssessmentQuestion.model_validate(item)
            for item in data
        ]
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("❌ Failed to fetch assessment quiz")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Failed to fetch assessment quiz.",
        ) from exc

@router.post(
    "/assessment_submit", 
    response_model=AssessmentResult,
    operation_id="submit_assessment_quiz"
)
async def submit_assessment_quiz(
    payload: AssessmentPayload, 
    user=Depends(require_role(["Learner"])),
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db)
) -> AssessmentResult:
    """Submit the assessment quiz answers for the authenticated user."""
    try:
        logger.info(f"ℹ️ Submitting assessment quiz for user: {user['email']} with {len(payload.answers)} answers")
        
        user_profile = await _get_current_user_profile(user, db)
        
        data = await submit_assessment_quiz_for_user(
            payload=payload, 
            user_id=user_profile.user_id, 
            db=db, 
            response_language=response_language
        )

        logger.info(f"✅ Successfully submitted assessment quiz for user: {user['email']} with result: {data.knowledge_assessment} and {len(data.recommended_courses)} recommended courses")
        
        return data
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("❌ Failed to submit assessment quiz")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Failed to submit assessment quiz.",
        ) from exc

@router.get(
    "/questions", 
    response_model=list[AssessmentAdminQuestionResponse],
    operation_id="list_assessment_questions_admin"
)
async def get_questions_admin(
    user=Depends(require_role(["Admin"])),
    db: AsyncSession = Depends(get_db),
) -> list[AssessmentAdminQuestionResponse]:
    """Fetch all assessment questions (Admin only)."""
    try:
        logger.info(f"ℹ️ Fetching all assessment questions for admin user: {user['email']}")

        questions = await list_all_questions(db)

        logger.info(f"✅ Successfully fetched {len(questions)} assessment questions for admin user: {user['email']}")
        
        return [
            AssessmentAdminQuestionResponse.model_validate(question)
            for question in questions
        ]
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("❌ Failed to fetch assessment questions")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Failed to fetch assessment questions.",
        ) from exc

@router.get(
    "/config",
    response_model=AssessmentConfigResponse,
    operation_id="get_assessment_config_admin"
)
async def get_config_admin(
    user=Depends(require_role(["Admin"])),
    db: AsyncSession = Depends(get_db),
) -> AssessmentConfigResponse:
    """Fetch the assessment configuration (Admin only)."""
    try:
        logger.info(f"ℹ️ Fetching assessment configuration for admin user: {user['email']}")

        config = await fetch_config(db)

        logger.info(f"✅ Successfully fetched assessment configuration for admin user: {user['email']} with config keys: {list(config.keys()) if config else 'N/A'}")
        
        return AssessmentConfigResponse(config=config or {})
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("❌ Failed to fetch assessment configuration")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Failed to fetch assessment configuration.",
        ) from exc

@router.put(
    "/config", 
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="update_assessment_config_admin"
)
async def put_config_admin(
    payload: AssessmentConfigUpdateRequest,
    user=Depends(require_role(["Admin"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Update the assessment configuration (Admin only)."""
    try:
        logger.info(f"ℹ️ Updating assessment configuration for admin user: {user['email']} with config keys: {list(payload.config.keys()) if payload.config else 'N/A'}")
        
        await update_config(payload.config, db)

        logger.info(f"✅ Successfully updated assessment configuration for admin user: {user['email']}")
        
        return None
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("❌ Failed to update assessment configuration")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Failed to update assessment configuration.",
        ) from exc

# OPTIONAL: allow deleting a question
@router.delete(
    "/questions/{question_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_assessment_question_admin"
)
async def delete_question_admin(
    question_id: int = Path(..., gt=0),
    user=Depends(require_role(["Admin"])),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an assessment question by ID (Admin only)."""
    try:
        logger.info(f"ℹ️ Deleting assessment question with ID: {question_id} for admin user: {user['email']}")
        
        await remove_question(question_id, db)

        logger.info(f"✅ Successfully deleted assessment question with ID: {question_id} for admin user: {user['email']}")
        
        return None
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("❌ Failed to delete assessment question")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Failed to delete assessment question.",
        ) from exc
