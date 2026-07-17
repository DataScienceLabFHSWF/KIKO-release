from pydantic import BaseModel, Field
from typing import Optional, Any

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
