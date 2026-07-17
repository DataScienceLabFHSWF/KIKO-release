import logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import get_instructor_statistics, require_role
from app.schemas import InstructorStatistics

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/dashboard")
async def instructor_dashboard(
    user=Depends(require_role(["Instructor"]))
):
    """Instructor dashboard with course management and statistics."""
    print(f"ℹ️ Instructor dashboard accessed by user: {user}")
    return {"message": f"Welcome Instructor: {user}"}

@router.get("/statistics", response_model=InstructorStatistics)
async def get_instructor_stats(
    user=Depends(require_role(["Instructor"])), 
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for the instructor dashboard."""
    print(f"ℹ️ Fetching instructor statistics for user: {user}")
    # Fetch instructor statistics using the service function
    return await get_instructor_statistics(user["email"], db)

@router.get("/queries")
async def get_queries(
    user=Depends(require_role(["Instructor"]))
):
    """Get recent queries made by learners."""
    print(f"ℹ️ Fetching recent queries for user: {user}")

    dummy_queries = [
        {
            "username": "learner1",
            "role": "Learner",
            "question": "What is nuclear fusion?",
            "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        },
        {
            "username": "learner2",
            "role": "Learner",
            "question": "How does a reactor work?",
            "timestamp": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        },
        {
            "username": "learner3",
            "role": "Learner",
            "question": "Explain neutron moderation?",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "username": "learner1",
            "role": "Learner",
            "question": "Explain Nuclear Decomissioning?",
            "timestamp": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat()
        },
        {
            "username": "learner3",
            "role": "Learner",
            "question": "Explain Nuclear Raditions?.",
            "timestamp": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
        },
        {
            "username": "learner2",
            "role": "Learner",
            "question": "Explain Nuclear refactors?",
            "timestamp": (datetime.now(timezone.utc) - timedelta(hours=10)).isoformat()
        },
    ]

    return dummy_queries
