from pydantic import BaseModel
from typing import List, Optional
from .grade_schema import GradedAnswer

class AssessmentQuestion(BaseModel):
    """Schema for an assessment question.
    This Schema represents a knowledge assessment question,
    including its ID, topic, question text, and type."""
    
    question_id: int
    topic: str
    question: str
    type: str

class AssessmentPayload(BaseModel):
    """Payload Schema for knowledge assessment.
    This Schema includes a list of answers provided by the user
    for the assessment questions."""
    
    answers: List[dict]

class RecommendedCourse(BaseModel):
    """Schema for a recommended course.
    This Schema represents a course recommended to the user
    based on their assessment results, including course ID, title,
    summary, reason for recommendation, and a score."""
    
    course_id: int
    title: str
    summary: Optional[str] = None
    reason: Optional[str] = None
    # keep score 0..1 if you’re using overlap or cosine similarity
    score: float

class AssessmentResult(BaseModel):
    """Schema for knowledge assessment results.
    This Schema represents the results of a knowledge assessment,
    including graded answers, overall assessment, learning path,
    learning step, and recommended courses."""
    
    graded_answers: List[GradedAnswer]
    knowledge_assessment: str
    learning_path: str
    learning_step: str
    recommended_courses: List[RecommendedCourse]
