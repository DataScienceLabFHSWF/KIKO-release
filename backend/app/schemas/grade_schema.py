from pydantic import BaseModel

class GradePayload(BaseModel):
    """Payload Schema for grading answers.
    This Schema includes fields for the question text, reference answer, user answer,
    and the name of the reasoning model used for grading."""
    
    question: str
    reference_answer: str | None = None
    user_answer: str
    reasoning_model_name: str

class GradedAnswer(BaseModel):
    """Schema for a graded answer.
    This Schema represents the result of grading a user's answer,
    including the question ID, assigned grade, and a summary of the grading."""
    
    question_id: int
    grade: int
    summary: str
