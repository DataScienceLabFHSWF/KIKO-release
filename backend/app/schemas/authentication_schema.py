# backend/app/schemas/authentication_schema.py
from pydantic import BaseModel, constr
from typing import Any, Literal

UserRole = Literal["Learner", "Instructor", "Admin"]

class UserLoginRequest(BaseModel):
    """UserLoginRequest Schema for user authentication.
    This schema is used to represent the credentials required for user login.
    It includes the username or email and password fields."""
    
    email: str
    password: str

class UserLoginResponse(BaseModel):
    """UserLoginResponse Schema for user authentication.
    This schema is used to represent the response returned upon successful user authentication.
    It includes the access token string and the token type."""
    
    access_token: str
    token_type: str

class UserRegisterRequest(BaseModel):
    """Schema for user registration request.
    This Schema includes fields required for registering a new user,
    such as username, email, date of birth, password, role, full name, and bio."""
    
    # username: constr(strip_whitespace=True, min_length=3, max_length=64)
    email: str
    # date_of_birth: date | None = None
    password: constr(min_length=8)  # adjust strength rules if needed
    role: UserRole
    full_name: constr(strip_whitespace=True, min_length=3, max_length=128)
    # bio: str

class UserPublicResponse(BaseModel):
    """Schema for public user information.
    This schema is used to represent the public information of a user,
    excluding sensitive data like password. It includes user ID, email, role, full name, and avatar URL."""
    user_id: int
    email: str
    role: UserRole
    full_name: str
    avatar: str | None = None
    email_verified: bool = False

class UserRegisterResponse(BaseModel):
    """Schema for user registration response.
    This schema is used to represent the response returned upon successful user registration.
    It includes a success message, the registered user's public information, and a report of default course creation."""
    message: Literal["success"]
    user: UserPublicResponse
    default_course_report: dict[str, Any] | None = None

class GenericSuccessResponse(BaseModel):
    message: Literal["success"] = "success"

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: constr(min_length=20)
    new_password: constr(min_length=8)

class ChangePasswordRequest(BaseModel):
    current_password: constr(min_length=8)
    new_password: constr(min_length=8)

class ChangePasswordResponse(BaseModel):
    message: Literal["success"]
    access_token: str
    token_type: Literal["bearer"] = "bearer"

class VerifyEmailRequest(BaseModel):
    token: constr(min_length=20)

class ResendVerificationEmailRequest(BaseModel):
    email: str
