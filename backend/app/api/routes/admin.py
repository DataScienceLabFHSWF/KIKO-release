import logging
from fastapi import APIRouter, Depends
from datetime import datetime, timedelta, timezone
from app.services import require_role

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/dashboard")
async def learner_dashboard(
    user=Depends(require_role(["Admin"]))
):
    """Admin dashboard with system stats and user management."""
    print(f"ℹ️ Admin dashboard accessed by user: {user}")
    return {"message": f"Welcome Admin: {user}"}

@router.get("/stats")
async def get_admin_stats(
    user=Depends(require_role(["Admin"]))
):
    """Get system statistics for the admin dashboard."""
    print(f"ℹ️ Fetching admin stats for user: {user}")
    
    return {
        "documents_uploaded": 5,
        "users_registered": 10,
        "pipelines_status": "All systems operational",   
        "system_uptime": "99.9%",
        "last_activity": str(datetime.now(timezone.utc)),
    }

@router.get("/logs")
async def get_upload_logs(
    user=Depends(require_role(["Admin"]))
):
    """Get recent upload logs for the admin dashboard."""
    print(f"ℹ️ Fetching upload logs for user: {user}")
    
    dummy_uploads = [
        {
            "filename": "nuclear_basics.pdf",
            "uploaded_by": "learner1",
            "timestamp": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        },
        {
            "filename": "fusion_safety.docx",
            "uploaded_by": "instructor1",
            "timestamp": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
        },
        {
            "filename": "fission_reactor_design.xlsx",
            "uploaded_by": "learner1",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "filename": "nuclear_decay_model.csv",
            "uploaded_by": "instructor1",
            "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        },
        {
            "filename": "isotope_tracking_v1.json",
            "uploaded_by": "instructor1",
            "timestamp": (datetime.now(timezone.utc) - timedelta(hours=10)).isoformat()
        },
        {
            "filename": "facility_radiation_report_2025.xlsx",
            "uploaded_by": "learner1",
            "timestamp": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat()
        },
        {
            "filename": "containment_status_report.txt",
            "uploaded_by": "instructor1",
            "timestamp": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        },
        {
            "filename": "uranium_enrichment_stats.csv",
            "uploaded_by": "instructor1",
            "timestamp": (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        }
    ]

    return dummy_uploads
