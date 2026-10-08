# backend/app/schemas/admin_schema.py
from datetime import datetime
from pydantic import BaseModel

class AdminDashboardResponse(BaseModel):
    message: str

class AdminStatsResponse(BaseModel):
    users_registered: int
    learners_registered: int = 0
    instructors_registered: int = 0
    admins_registered: int = 0
    documents_uploaded: int
    courses_created: int = 0
    chat_questions: int = 0
    pipelines_status: str
    system_uptime: str
    last_activity: datetime

class AdminUploadLogResponse(BaseModel):
    filename: str
    uploaded_by: str
    timestamp: datetime

class AdminUploadLogsResponse(BaseModel):
    logs: list[AdminUploadLogResponse]
