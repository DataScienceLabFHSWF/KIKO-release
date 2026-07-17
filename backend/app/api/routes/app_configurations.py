import logging
from fastapi import APIRouter, Depends
from app.services import require_role, get_app_config_and_libary_available

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/app_config")
async def get_app_config(
    user=Depends(require_role(["Learner", "Instructor", "Admin"]))
):
    """API to read and create the the app configurations."""
    print("ℹ️ API: Reading and creating the the app configurations.")
    
    configurations = await get_app_config_and_libary_available()

    if configurations is None:
        print("❌ API: Error while reading the app configurations.")
        return {"error": "Failed to retrieve application configurations."}
    print(f"✅ API: Successfully created the app configurations: {configurations}.")    
    return configurations
