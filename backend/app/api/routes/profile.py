# backend/app/api/routes/profile.py

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserProfileResponse, COMMON_ERROR_RESPONSES, UserProfileUpdateRequest
from app.database import get_db
from app.services import get_user_profile_by_email, require_role, update_current_user_profile

logger = logging.getLogger(__name__)

router = APIRouter(responses=COMMON_ERROR_RESPONSES)

@router.get(
    "/user_info", 
    response_model=UserProfileResponse,
    response_model_exclude_none=True,
    operation_id="get_current_user_profile"
)
async def get_user_info(
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    db: AsyncSession = Depends(get_db)
) -> UserProfileResponse:
    """
    Get user profile information by email.
    Requires user to be authenticated and have a valid role.
    """
    try:
        logger.info(f"ℹ️ Fetching user profile for USER : {user['email']}")

        db_user = await get_user_profile_by_email(user["email"], db)

        logger.info(f"✅ User profile retrieved for USER : {user['email']} with data: {db_user}")
        
        return UserProfileResponse.model_validate(db_user)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ Unexpected error while fetching user profile")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Unexpected error while fetching user profile.",
        ) from e

@router.patch(
    "/user_info",
    response_model=UserProfileResponse,
    operation_id="update_current_user_profile",
)
async def update_user_info(
    payload: UserProfileUpdateRequest,
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    try:
        updated_user = await update_current_user_profile(
            email=user["email"],
            payload=payload,
            db=db,
        )
        
        return UserProfileResponse.model_validate(updated_user)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ Unexpected error while updating the user profile")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Unexpected error while updating the user profile.",
        ) from e
