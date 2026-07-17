# Entry point for FastAPI application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import (
    authentication, profile, document, learner,
    instructor, admin, chatbot, app_configurations, 
    files, course, knowledge_assessment
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
def health_check():
    return {"message": "Backend is up"}

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
