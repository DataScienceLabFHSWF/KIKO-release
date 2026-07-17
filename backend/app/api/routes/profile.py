import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserProfile
from app.database import get_db
from app.services import get_user_profile_by_email, require_role

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/user_info", response_model=UserProfile)
async def get_user_info(
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user profile information by email.
    Requires user to be authenticated and have a valid role.
    """
    db_user = await get_user_profile_by_email(user["email"], db)
    
    return db_user
