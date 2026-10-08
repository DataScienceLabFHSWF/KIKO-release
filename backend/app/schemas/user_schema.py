# backend/app/schemas/user_schema.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Literal
from datetime import datetime

UserRole = Literal["Learner", "Instructor", "Admin"]

class UserProfileResponse(BaseModel):
    """UserProfileResponse Schema for representing user information.
    This schema includes fields for user identification, personal details, and account status.
    It is used to manage user profiles within the application."""

    model_config = ConfigDict(from_attributes=True)

    # username: str
    user_id: int
    email: str
    # date_of_birth: date
    full_name: str
    role: UserRole
    avatar: str | None = None
    # bio: Optional[str]
    joined: datetime
    last_login: Optional[datetime] = None

class UserProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(
        default=None,
        min_length=3,
        max_length=128,
    )
    avatar: str | None = Field(
        default=None,
        max_length=512,
    )
