# backend/app/main.py
# Entry point for FastAPI application
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import (
    authentication, profile, document, learner,
    instructor, admin, chatbot, app_configurations, 
    files, course, knowledge_assessment
)
from app.schemas import (
    ApiError, ApiErrorResponse, HealthCheckResponse
)
from app.core import configure_logging

configure_logging()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get(
    "/",
    response_model=HealthCheckResponse,
    operation_id="get_health_check"
)
def health_check() -> HealthCheckResponse:
    return HealthCheckResponse(status="⚡ FastAPI Backend is up 🚀")

@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, 
    exc: HTTPException
):
    request_id = str(uuid4())

    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
    details = None if isinstance(exc.detail, str) else exc.detail

    payload = ApiErrorResponse(
        error=ApiError(
            code=f"HTTP_{exc.status_code}",
            message=message,
            details=details,
            request_id=request_id,
        )
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=payload.model_dump(),
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
):
    request_id = str(uuid4())

    payload = ApiErrorResponse(
        error=ApiError(
            code="VALIDATION_ERROR",
            message="❌ Invalid request payload.",
            details=exc.errors(),
            request_id=request_id,
        )
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=payload.model_dump(),
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, 
    exc: Exception
):
    request_id = str(uuid4())

    payload = ApiErrorResponse(
        error=ApiError(
            code="INTERNAL_SERVER_ERROR",
            message="Unexpected server error.",
            details=str(exc),
            request_id=request_id,
        )
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=payload.model_dump(),
    )

# Common modules in all roles. 
# These modules are accessible to all roles and are not role-specific.
app.include_router(authentication.router, prefix="/api/authentication")
app.include_router(profile.router, prefix="/api/profile")
app.include_router(document.router, prefix="/api/document")
app.include_router(chatbot.router, prefix="/api/chatbot")
app.include_router(app_configurations.router, prefix="/api/app_configurations")
app.include_router(files.router, prefix="/api/files")

# Role-based modules

# Learner modules
app.include_router(learner.router, prefix="/api/learner")
app.include_router(knowledge_assessment.router, prefix="/api/knowledge_assessment")

# Instructor modules
app.include_router(instructor.router, prefix="/api/instructor")
app.include_router(course.router, prefix="/api/course")

# Admin modules
app.include_router(admin.router, prefix="/api/admin")
