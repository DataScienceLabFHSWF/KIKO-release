from pydantic import BaseModel, constr
from typing import Optional
from datetime import datetime, date

AllowedRole = constr(pattern=r"^(Learner|Instructor|Admin)$")

class UserProfile(BaseModel):
    """UserProfile Schema for representing user information.
    This schema includes fields for user identification, personal details, and account status.
    It is used to manage user profiles within the application."""

    # username: str
    email: str
    password: str
    # date_of_birth: date
    full_name: str
    role: str
    avatar: Optional[str]
    # bio: Optional[str]
    joined: datetime
    last_login: Optional[datetime] = None

class UserLogin(BaseModel):
    """UserLogin Schema for user authentication.
    This schema is used to represent the credentials required for user login.
    It includes the username or email and password fields."""
    
    email: str
    password: str

class RegisterRequest(BaseModel):
    """Schema for user registration request.
    This Schema includes fields required for registering a new user,
    such as username, email, date of birth, password, role, full name, and bio."""
    
    # username: constr(strip_whitespace=True, min_length=3, max_length=64)
    email: str
    # date_of_birth: date | None = None
    password: constr(min_length=8)  # adjust strength rules if needed
    role: AllowedRole
    full_name: constr(strip_whitespace=True, min_length=3, max_length=128)
    # bio: str
