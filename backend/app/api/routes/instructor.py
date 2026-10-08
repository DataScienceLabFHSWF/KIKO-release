# backend/app/api/routes/instructor.py

import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import get_instructor_statistics, require_role
from app.schemas import (
    InstructorStatistics, COMMON_ERROR_RESPONSES, InstructorDashboardResponse,
    InstructorLearnerQueryResponse, InstructorRecentQueriesResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(responses=COMMON_ERROR_RESPONSES)

@router.get(
    "/dashboard",
    response_model=InstructorDashboardResponse,
    operation_id="get_instructor_dashboard"
)
async def instructor_dashboard(
    user=Depends(require_role(["Instructor"]))
) -> InstructorDashboardResponse:
    """Instructor dashboard with course management and statistics."""

    logger.info(f"ℹ️ Instructor dashboard accessed by user: {user}")
    
    return InstructorDashboardResponse(
        message=f"Welcome Instructor: {user['email']}"
    )

@router.get(
    "/statistics", 
    response_model=InstructorStatistics,
    operation_id="get_instructor_statistics"
)
async def get_instructor_stats(
    user=Depends(require_role(["Instructor"])), 
    db: AsyncSession = Depends(get_db)
) -> InstructorStatistics:
    """Get statistics for the instructor dashboard."""
    try:

        logger.info(f"ℹ️ Fetching instructor statistics for user: {user}")
        
        stats = await get_instructor_statistics(user["email"], db)

        logger.info(f"✅ Successfully fetched instructor statistics for user: {user}, stats: {stats}")
        
        return InstructorStatistics.model_validate(stats)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("❌ Failed to fetch instructor statistics")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Failed to fetch instructor statistics.",
        ) from exc

@router.get(
    "/queries",
    response_model=InstructorRecentQueriesResponse,
    operation_id="list_recent_learner_queries"
)
async def get_queries(
    user=Depends(require_role(["Instructor"]))
) -> InstructorRecentQueriesResponse:
    """Get recent queries made by learners."""
    try:

        logger.info(f"ℹ️ Fetching recent queries for user: {user}")
        
        # future DB-backed version
        # rows = await list_recent_learner_queries_for_instructor(
        #     instructor_email=user["email"],
        #     db=db,
        # )
        
        # return InstructorRecentQueriesResponse(
        #     queries=[
        #         InstructorLearnerQueryResponse.model_validate(row)
        #         for row in rows
        #     ]
        # )
            
        now = datetime.now(timezone.utc)
        
        queries = [
            InstructorLearnerQueryResponse(
                username="learner1",
                role="Learner",
                question="What is nuclear fusion?",
                timestamp=now - timedelta(hours=2),
            ),
            InstructorLearnerQueryResponse(
                username="learner2",
                role="Learner",
                question="How does a reactor work?",
                timestamp=now - timedelta(hours=1),
            ),
            InstructorLearnerQueryResponse(
                username="learner3",
                role="Learner",
                question="Explain neutron moderation?",
                timestamp=now,
            ),
            InstructorLearnerQueryResponse(
                username="learner1",
                role="Learner",
                question="Explain nuclear decommissioning?",
                timestamp=now - timedelta(hours=4),
            ),
            InstructorLearnerQueryResponse(
                username="learner3",
                role="Learner",
                question="Explain nuclear radiation?",
                timestamp=now - timedelta(hours=6),
            ),
            InstructorLearnerQueryResponse(
                username="learner2",
                role="Learner",
                question="Explain nuclear reactors?",
                timestamp=now - timedelta(hours=10),
            ),
        ]

        logger.info(f"✅ Successfully fetched {len(queries)} recent queries for user: {user}")

        return InstructorRecentQueriesResponse(queries=queries)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("❌ Failed to fetch recent learner queries")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="❌ Failed to fetch recent learner queries.",
        ) from exc
