from pydantic import BaseModel, Field
from typing import Any
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
