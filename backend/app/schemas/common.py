# backend/app/schemas/common.py
from typing import Any
from pydantic import BaseModel, Field

class ApiError(BaseModel):
    """Schema for API error responses.
    This schema is used to represent the structure of error responses returned by the API.
    It includes an error code, a human-readable message, optional details about the error, and an optional request ID for tracing."""

    code: str = Field(..., examples=["COURSE_NOT_FOUND", "VALIDATION_ERROR"])
    message: str
    details: Any | None = None
    request_id: str | None = None

class ApiErrorResponse(BaseModel):
    """Schema for API error response wrapper.
    This schema is used to represent the standard structure of error responses returned by the API.
    It includes a success flag (always false for errors) and an error object containing the error details."""
    error: ApiError

COMMON_ERROR_RESPONSES = {
    400: {"model": ApiErrorResponse},
    401: {"model": ApiErrorResponse},
    403: {"model": ApiErrorResponse},
    404: {"model": ApiErrorResponse},
    409: {"model": ApiErrorResponse},
    422: {"model": ApiErrorResponse},
    500: {"model": ApiErrorResponse},
}

class HealthCheckResponse(BaseModel):
    status: str
