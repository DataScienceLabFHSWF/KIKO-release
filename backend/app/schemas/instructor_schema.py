from pydantic import BaseModel
from datetime import datetime
from typing import Literal

class InstructorStatistics(BaseModel):
    """
    Schema for instructor statistics.
    This Schema includes various statistics related to the instructor's performance and activities.
    It is used to provide insights into the instructor's engagement with students and courses.
    """
    students: int
    courses_created: int
    questions_asked: int
    learner_questions: int
    documents_uploaded: int = 0
    last_activity: datetime

class InstructorDashboardResponse(BaseModel):
    """
    Schema for instructor dashboard response.
    This schema includes a welcome message for the instructor dashboard.
    It is used to provide a personalized greeting when the instructor accesses their dashboard.
    """
    message: str

class InstructorLearnerQueryResponse(BaseModel):
    """
    Schema for recent learner queries.
    This schema includes details about recent queries made by learners, such as the username, role, question, and timestamp.
    It is used to display recent learner queries to the instructor, allowing them to see what questions their students are asking.
    """
    username: str
    role: Literal["Learner"]
    question: str
    timestamp: datetime

class InstructorRecentQueriesResponse(BaseModel):
    """
    Schema for recent learner queries response.
    This schema includes a list of recent queries made by learners, each represented by the InstructorLearnerQueryResponse schema.
    It is used to provide a structured response containing recent learner queries for the instructor dashboard.
    """
    queries: list[InstructorLearnerQueryResponse]
