# backend/app/schemas/grade_schema.py

from pydantic import BaseModel, Field
from typing import Literal

class AnswerGradingRequest(BaseModel):
    """Payload Schema for grading answers.
    This Schema includes fields for the question text, reference answer, user answer,
    and the name of the reasoning model used for grading."""
    
    question: str
    reference_answer: str | None = None
    user_answer: str
    reasoning_model_name: str | None = None
    misconceptions: list[str] = Field(default_factory=list)

class AnswerGradingResponse(BaseModel):
    """Schema for a graded answer.
    This Schema represents the result of grading a user's answer,
    including the question ID, assigned grade, and a summary of the grading."""

    message: Literal["success"]
    grade: int
    summary: str
    misconceptions_considered: list[str] = Field(default_factory=list)
