# backend/app/services/admin_service.py
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from datetime import datetime, timezone
from app.schemas import AdminStatsResponse
from app.models import (
    UserModel, DocumentModel, CourseModel, 
    ChatHistoryModel
)

logger = logging.getLogger(__name__)

async def get_admin_statistics(db: AsyncSession) -> AdminStatsResponse:
    try:
        users_q = await db.execute(
            select(func.count())
            .select_from(UserModel)
        )

        learners_q = await db.execute(
            select(func.count())
            .select_from(UserModel)
            .where(UserModel.role == "Learner")
        )

        instructors_q = await db.execute(
            select(func.count())
            .select_from(UserModel)
            .where(UserModel.role == "Instructor")
        )

        admins_q = await db.execute(
            select(func.count())
            .select_from(UserModel)
            .where(UserModel.role == "Admin")
        )

        documents_q = await db.execute(
            select(func.count())
            .select_from(DocumentModel)
        )
        
        courses_q = await db.execute(
            select(func.count())
            .select_from(CourseModel)
        )

        chats_q = await db.execute(
            select(func.count())
            .select_from(ChatHistoryModel)
        )

        return AdminStatsResponse(
            users_registered=users_q.scalar() or 0,
            learners_registered=learners_q.scalar() or 0,
            instructors_registered=instructors_q.scalar() or 0,
            admins_registered=admins_q.scalar() or 0,
            documents_uploaded=documents_q.scalar() or 0,
            courses_created=courses_q.scalar() or 0,
            chat_questions=chats_q.scalar() or 0,
            pipelines_status="Operational",
            system_uptime="Available",
            last_activity=datetime.now(timezone.utc),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Unexpected error during get learner statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during get learner statistics: {str(e)}",
        ) from e
