# backend/app/api/routes/knowledge_assessment.py
import logging
from fastapi import APIRouter, HTTPException, Depends, status, Path
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from app.database import get_db
from app.services import (
    require_role, get_assessment_quiz_for_user, submit_assessment_quiz_for_user,
    get_user_profile_by_email, list_all_questions, fetch_config,
    update_config, remove_question, get_request_lang
)
from app.schemas import (AssessmentQuestion, AssessmentPayload, AssessmentResult)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/assessment_quiz", response_model=List[AssessmentQuestion])
async def get_assessment_quiz(
    user=Depends(require_role(["Learner"])),
    db: AsyncSession = Depends(get_db)
):
    """Fetch the assessment quiz for the authenticated user."""
    try:
        data = await get_assessment_quiz_for_user(db=db)
        return data
    except Exception as e:
        print(f"❌ /assessment_quiz error: {e}")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail":str(e)})

@router.post("/assessment_submit", response_model=AssessmentResult)
async def submit_assessment_quiz(
    payload: AssessmentPayload, 
    user=Depends(require_role(["Learner"])),
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db)
):
    """Submit the assessment quiz answers for the authenticated user."""
    try:
        email_address = user["email"]
        
        user_profile = await get_user_profile_by_email(email_address, db)
        
        if not user_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")
        
        data = await submit_assessment_quiz_for_user(payload=payload, user_id=user_profile.user_id, db=db, response_language=response_language)

        return data
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail":str(e)})

@router.get("/questions", response_model=List[Dict[str, Any]])
async def get_questions_admin(
    user=Depends(require_role(["Admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Fetch all assessment questions (Admin only)."""
    try:
        return await list_all_questions(db)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail":str(e)})

@router.get("/config")
async def get_config_admin(
    user=Depends(require_role(["Admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Fetch the assessment configuration (Admin only)."""
    try:
        return await fetch_config(db)
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail":str(e)})

@router.put("/config", status_code=status.HTTP_204_NO_CONTENT)
async def put_config_admin(
    payload: Dict[str, Any],
    user=Depends(require_role(["Admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Update the assessment configuration (Admin only)."""
    try:
        await update_config(payload, db)
        return
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail":str(e)})

# OPTIONAL: allow deleting a question
@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question_admin(
    question_id: int = Path(..., gt=0),
    user=Depends(require_role(["Admin"])),
    db: AsyncSession = Depends(get_db),
):
    """Delete an assessment question by ID (Admin only)."""
    try:
        await remove_question(question_id, db)
        return
    except Exception as e:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail":str(e)})
