# backend/app/schemas/knowledge_assessment_schema.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any
from datetime import datetime

class AssessmentQuestion(BaseModel):
    """
    Schema for an assessment question.
    This Schema represents a knowledge assessment question,
    including its ID, topic, question text, and type.
    """
    model_config = ConfigDict(from_attributes=True)
    question_id: int
    topic: str
    question: str
    type: str
    # Keep optional because question format may differ by type.
    options: list[dict[str, Any]] | None = None
    difficulty: str | None = None

class AssessmentAnswerItem(BaseModel):
    """
    One submitted answer.

    Keep extra='allow' during migration so old frontend payloads do not break
    immediately if they contain additional keys.
    """

    model_config = ConfigDict(extra="allow")

    question_id: int
    user_answer: Any | None = None
    selected_choice_ids: list[str] = Field(default_factory=list)
    selected_value: Any | None = None


class AssessmentPayload(BaseModel):
    """
    Payload Schema for knowledge assessment.
    This Schema includes a list of answers provided by the user
    for the assessment questions.
    """
    answers: list[AssessmentAnswerItem] = Field(default_factory=list)

class RecommendedCourse(BaseModel):
    """
    Schema for a recommended course.
    This Schema represents a course recommended to the user
    based on their assessment results, including course ID, title,
    summary, reason for recommendation, and a score.
    """
    model_config = ConfigDict(from_attributes=True)
    course_id: int
    title: str
    summary: Optional[str] = None
    reason: Optional[str] = None
    # keep score 0..1 if you’re using overlap or cosine similarity
    score: float = Field(..., ge=0.0, le=1.0)

class AssessmentGradedAnswerResponse(BaseModel):
    question_id: int
    grade: int | float
    summary: str = ""

class AssessmentResult(BaseModel):
    """
    Schema for knowledge assessment results.
    This Schema represents the results of a knowledge assessment,
    including graded answers, overall assessment, learning path,
    learning step, and recommended courses.
    """
    graded_answers: list[AssessmentGradedAnswerResponse] = Field(default_factory=list)
    knowledge_assessment: str
    learning_path: str
    learning_step: str
    recommended_courses: list[RecommendedCourse] = Field(default_factory=list)

class AssessmentAdminQuestionResponse(AssessmentQuestion):
    """
    Admin view can expose more fields than learner quiz view.
    Do not expose internal DB-only fields unless needed by frontend.
    """
    correct_answer: Any | None = None
    explanation: str | None = None
    is_active: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

class AssessmentConfigResponse(BaseModel):
    """
    Named config response for OpenAPI/React generation.
    If your config shape becomes stable later, replace config: dict[str, Any]
    with explicit fields such as max_questions, pass_threshold, etc.
    """
    config: dict[str, Any] = Field(default_factory=dict)

class AssessmentConfigUpdateRequest(BaseModel):
    """Named config request for OpenAPI/React generation.
    If your config shape becomes stable later, replace config: dict[str, Any]
    with explicit fields such as max_questions, pass_threshold, etc.
    """
    config: dict[str, Any] = Field(default_factory=dict)
