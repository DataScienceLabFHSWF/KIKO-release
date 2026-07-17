from pydantic import BaseModel
from datetime import datetime

class InstructorStatistics(BaseModel):
    """Schema for instructor statistics.
    This Schema includes various statistics related to the instructor's performance and activities.
    It is used to provide insights into the instructor's engagement with students and courses."""
    
    students: int
    courses_created: int
    questions_asked: int
    learner_questions: int
    last_activity: datetime
