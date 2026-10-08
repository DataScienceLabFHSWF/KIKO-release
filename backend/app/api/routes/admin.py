# backend/app/api/routes/admin.py

import logging
from fastapi import APIRouter, Depends
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import require_role, get_admin_statistics
from app.schemas import (
    COMMON_ERROR_RESPONSES, AdminDashboardResponse, AdminStatsResponse,
    AdminUploadLogResponse, AdminUploadLogsResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(responses=COMMON_ERROR_RESPONSES)

@router.get(
    "/dashboard",
    response_model=AdminDashboardResponse,
    operation_id="get_admin_dashboard"
)
async def admin_dashboard(
    user=Depends(require_role(["Admin"]))
) -> AdminDashboardResponse:
    """Admin dashboard with system stats and user management."""
    logger.info("ℹ️ Admin dashboard accessed by user: %s", user.get("email"))
    
    return AdminDashboardResponse(
        message=f"Welcome Admin: {user['email']}"
    )

@router.get(
    "/statistics",
    response_model=AdminStatsResponse,
    operation_id="get_admin_statistics"
)
async def admin_statistics(
    user=Depends(require_role(["Admin"])),
    db: AsyncSession = Depends(get_db)
) -> AdminStatsResponse:
    """Get system statistics for the admin dashboard."""
    
    logger.info("ℹ️ Fetching admin stats for user: %s", user.get("email"))

    return await get_admin_statistics(db)

@router.get(
    "/logs",
    response_model=AdminUploadLogsResponse,
    operation_id="get_admin_upload_logs"
)
async def admin_upload_logs(
    user=Depends(require_role(["Admin"]))
) -> AdminUploadLogsResponse:
    """Get recent upload logs for the admin dashboard."""
    
    logger.info("ℹ️ Fetching upload logs for user: %s", user.get("email"))

    now = datetime.now(timezone.utc)

    logs = [
        AdminUploadLogResponse(
            filename="nuclear_basics.pdf",
            uploaded_by="learner1",
            timestamp=now - timedelta(days=1),
        ),
        AdminUploadLogResponse(
            filename="fusion_safety.docx",
            uploaded_by="instructor1",
            timestamp=now - timedelta(hours=5),
        ),
        AdminUploadLogResponse(
            filename="fission_reactor_design.xlsx",
            uploaded_by="learner1",
            timestamp=now,
        ),
        AdminUploadLogResponse(
            filename="nuclear_decay_model.csv",
            uploaded_by="instructor1",
            timestamp=now - timedelta(hours=2),
        ),
        AdminUploadLogResponse(
            filename="isotope_tracking_v1.json",
            uploaded_by="instructor1",
            timestamp=now - timedelta(hours=10),
        ),
        AdminUploadLogResponse(
            filename="facility_radiation_report_2025.xlsx",
            uploaded_by="learner1",
            timestamp=now - timedelta(hours=6),
        ),
        AdminUploadLogResponse(
            filename="containment_status_report.txt",
            uploaded_by="instructor1",
            timestamp=now - timedelta(days=2),
        ),
        AdminUploadLogResponse(
            filename="uranium_enrichment_stats.csv",
            uploaded_by="instructor1",
            timestamp=now - timedelta(days=3),
        ),
    ]
    
    return AdminUploadLogsResponse(logs=logs)
