# backend/app/schemas/learner_schema.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Literal
from datetime import datetime

class LearnerStatistics(BaseModel):
    """Schema for learner statistics.
    This schema includes various statistics related to the learner's performance and activities.
    It is used to provide insights into the learner's engagement with courses and exams."""
    
    courses_enroll: int
    courses_completed: int
    courses_inprogress: int
    courses_progress_percent: int # Percentage of courses in progress
    exams_passed: int
    exams_failed: int
    exams_inprogress: int
    questions_asked: int
    documents_uploaded: int
    last_activity: datetime

class LearnerQuizAnswerItem(BaseModel):
    item_id: str
    selected_choice_ids: list[str] = Field(default_factory=list)
    selected_value: Any | None = None

class LearnerSubmitQuizRequest(BaseModel):
    assessment_id: str
    reasoning_model_name: str | None = None
    answers: list[LearnerQuizAnswerItem] = Field(default_factory=list)

class LearnerProgressUpdateRequest(BaseModel):
    """Schema for updating learner progress.
    This schema includes the current navigation state, current module ID, and any practice answers for quizzes.
    It is used to update the learner's progress in a course, allowing the backend to track their current position 
    and any answers they have submitted for practice quizzes."""
    current_nav: str | None = None
    current_module_id: str | None = None
    practice_answers: dict[str, Any] | None = None

class LearnerDashboardResponse(BaseModel):
    message: str

class LearnerCourseSummaryResponse(BaseModel):
    course_id: int
    title: str
    summary: str | None = None
    completion_percent: float = 0.0
    status: str | None = None
    completed: bool = False
    updated_at: datetime | None = None

class LearnerRecommendedCourseResponse(BaseModel):
    course_id: int
    title: str
    summary: str | None = None
    reason: str | None = None
    score: float | None = None

class LearnerAvailableCourseResponse(BaseModel):
    course_id: int
    title: str
    summary: str | None = None
    instructor_name: str | None = None
    is_enrolled: bool = False

class LearnerCourseProgressResponse(BaseModel):
    current_nav: str | None = None
    current_module_id: str | None = None
    progress_percent: int = 0
    practice_answers: dict[str, Any] | None = None
    updated_at: datetime | None = None

class CourseSummaryResponse(BaseModel):
    course_id: int
    title: str
    summary: str | None = None
    created_at: str | None = None

    model_config = ConfigDict(extra="ignore")

class LearnerCourseEnrollmentResponse(BaseModel):
    is_enrolled: bool = False
    enrolled: bool = False
    status: str = "not_enrolled"
    completion_percent: float = 0.0
    completed: bool = False

    model_config = ConfigDict(extra="ignore")

class LearnerProgressSnapshotResponse(BaseModel):
    current_nav: str | None = None
    current_module_id: str | None = None
    completion_percent: int | float | None = None
    module_status: dict[str, Any] = Field(default_factory=dict)
    final_status: dict[str, Any] = Field(default_factory=dict)
    practice_answers: dict[str, Any] = Field(default_factory=dict)
    course_completion: dict[str, Any] = Field(default_factory=dict)

class LearnerAttemptSummariesResponse(BaseModel):
    module_quizzes: dict[str, Any] = Field(default_factory=dict)
    final_quiz: dict[str, Any] = Field(default_factory=dict)
    course_completion: dict[str, Any] = Field(default_factory=dict)

class LearnerGradedAnswerResponse(BaseModel):
    item_id: str | None = None
    prompt: str | None = None
    question: str | None = None
    type: str | None = None
    awarded_points: int | float | None = None
    max_points: int | float | None = None
    correct: bool | None = None
    summary: str | None = None
    grade: int | float | str | None = None

class LearnerPersistedQuizAttemptResponse(BaseModel):
    attempt_id: int | None = None
    assessment_type: str | None = None
    assessment_id: str
    module_id: str | None = None
    submitted_answers: list[LearnerQuizAnswerItem] = Field(default_factory=list)

    score: int | float | None = None
    max_score: int | float | None = None
    percent: int | float | None = None
    passed: bool | None = None
    german_grade: int | float | str | None = None

    graded_answers: list[LearnerGradedAnswerResponse] = Field(default_factory=list)
    submitted_at: str | None = None

    model_config = ConfigDict(extra="ignore")

class LearnerLatestAttemptsResponse(BaseModel):
    module_quizzes: dict[str, LearnerPersistedQuizAttemptResponse] = Field(
        default_factory=dict
    )
    final_quiz: LearnerPersistedQuizAttemptResponse | None = None

class LearnerCourseDetailsResponse(BaseModel):
    course: CourseSummaryResponse
    enrollment: LearnerCourseEnrollmentResponse
    course_json: dict[str, Any] = Field(default_factory=dict)
    template_markdown: str = ""
    progress_snapshot: LearnerProgressSnapshotResponse = Field(
        default_factory=LearnerProgressSnapshotResponse
    )
    attempt_summaries: LearnerAttemptSummariesResponse = Field(
        default_factory=LearnerAttemptSummariesResponse
    )
    latest_attempts: LearnerLatestAttemptsResponse = Field(
        default_factory=LearnerLatestAttemptsResponse
    )

    model_config = ConfigDict(extra="ignore")

class LearnerQuizResultResponse(BaseModel):
    assessment_type: str
    assessment_id: str
    module_id: str | None = None
    score: int | float | None = None
    total_points: int | float | None = None
    percent: int | float | None = None
    passed: bool | None = None
    pass_percent: int | float | None = None
    german_grade: int | float | str | None = None
    feedback: list[LearnerGradedAnswerResponse] = Field(default_factory=list)

class LearnerProgressSaveResponse(BaseModel):
    message: Literal["Progress saved"]
    progress_snapshot: LearnerCourseProgressResponse | dict[str, Any]

class LearnerQuizSubmitResponse(BaseModel):
    message: str

    # Flat fields for easy frontend rendering
    course_id: int
    assessment_id: str
    module_id: str | None = None
    score: int | float | None = None
    max_score: int | float | None = None
    percent: int | float | None = None
    passed: bool | None = None
    pass_percent: int | float | None = None
    german_grade: int | float | str | None = None
    graded_answers: list[LearnerGradedAnswerResponse] = Field(default_factory=list)

    # Rich fields for progress refresh / future UI
    result: LearnerQuizResultResponse | None = None
    progress_snapshot: LearnerProgressSnapshotResponse | None = None
    attempt_summaries: LearnerAttemptSummariesResponse | None = None
