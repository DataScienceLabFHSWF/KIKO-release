# backend/app/api/routes/app_configurations.py

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import (
    require_role,
    get_app_config_and_libary_available,
    get_user_profile_by_email,
    update_app_config_for_admin,
)
from app.schemas import (
    COMMON_ERROR_RESPONSES,
    AppConfigResponse,
    AppConfigUpdateRequest,
    AppConfigUpdateResponse,
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
    "/app_config",
    response_model=AppConfigResponse,
    operation_id="get_app_config",
)
async def app_configurations(
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    db: AsyncSession = Depends(get_db),
) -> AppConfigResponse:
    """
    Read effective application configuration.

    Effective config = code defaults + admin-managed persisted overrides.
    """

    logger.info("ℹ️ API: Reading application configuration.")

    configurations = await get_app_config_and_libary_available(db=db)

    if configurations is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Failed to retrieve application configurations.",
        )

    response = AppConfigResponse.model_validate(configurations)

    logger.info("✅ API: Application configuration returned successfully.")

    return response

@router.put(
    "/app_config",
    response_model=AppConfigUpdateResponse,
    operation_id="update_app_config",
)
async def update_app_config(
    payload: AppConfigUpdateRequest,
    user=Depends(require_role(["Admin"])),
    db: AsyncSession = Depends(get_db),
) -> AppConfigUpdateResponse:
    """
    Update admin-editable application configuration.

    Only Admin can update.
    Only whitelisted fields are accepted.
    Runtime/system fields are intentionally not editable.
    """

    logger.info("ℹ️ API: Updating application configuration.")

    user_profile = await _get_current_user_profile(user, db)

    configurations = await update_app_config_for_admin(
        editable_config=payload.app_config,
        updated_by=user_profile.user_id,
        db=db,
    )

    response = AppConfigUpdateResponse.model_validate(
        {
            **configurations,
            "message": "success",
        }
    )

    logger.info(
        "✅ API: Application configuration updated successfully "
        f"by admin user_id={user_profile.user_id}."
    )

    return response
