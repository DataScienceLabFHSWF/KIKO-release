from typing import Annotated, Any, Literal, Optional

from fastapi import UploadFile
from pydantic import BaseModel, Field

from .app_config_schema import AppConfigSchema
from .qa_structure_schema import QuestionAnswerList


_COURSE_GENERATION_CONFIG = AppConfigSchema()


class CourseUploadPdfJobRequest(BaseModel):
    """Multipart fields used to start an asynchronous PDF course upload job."""

    file: UploadFile
    embedding_model_name: str
    llm_model_name: str
    qa_count: int = (
        _COURSE_GENERATION_CONFIG.course_generator_qa_count_default
    )
    quiz_question_count: int = (
        _COURSE_GENERATION_CONFIG.course_generator_quiz_question_count_default
    )
    quiz_option_count: int = (
        _COURSE_GENERATION_CONFIG.course_generator_quiz_option_count_default
    )
    misconception_count: int = (
        _COURSE_GENERATION_CONFIG.course_generator_misconception_count_default
    )


class CourseUploadJobSuccessResult(BaseModel):
    """Generated course content returned by a completed upload job."""

    message: Literal["success"]
    final_summary: str | None = None
    questions: QuestionAnswerList | None = None
    quiz: str | None = None
    generated_markdown: str | None = None
    generated_markdown_file_name: str | None = None
    metadata: dict[str, Any] | None = None
    template_markdown: str | None = None
    course_json: dict[str, Any] | None = None


class CourseUploadJobFileExistsResult(BaseModel):
    """Result returned when the uploaded PDF was already processed."""

    message: Literal["file_exists"]
    detail: str


CourseUploadJobResult = Annotated[
    CourseUploadJobSuccessResult | CourseUploadJobFileExistsResult,
    Field(discriminator="message"),
]

CourseUploadJobStatus = Literal[
    "queued",
    "processing",
    "cancelling",
    "completed",
    "cancelled",
    "failed",
]


class CourseUploadJobResponse(BaseModel):
    """Current state and optional result of a PDF course upload job."""

    job_id: str
    status: CourseUploadJobStatus
    progress: float = Field(ge=0.0, le=1.0)
    message: str
    cancel_requested: bool
    stage_key: str
    created_at: str = Field(description="ISO 8601 creation timestamp")
    updated_at: str = Field(description="ISO 8601 last-update timestamp")
    result: CourseUploadJobResult | None = None
    error: str | None = None


class CourseQuestionUpdate(BaseModel):
    question_id: Optional[int] = None
    text: str = Field(default="")
    answer_text: str = Field(default="")


class CourseUpdateRequest(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    quiz: Optional[str] = None
    template_markdown: Optional[str] = None
    course_json: Optional[dict[str, Any]] = None
    questions: Optional[list[CourseQuestionUpdate]] = None
