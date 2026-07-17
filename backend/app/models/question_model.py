from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.database import Base

class QuestionModel(Base):
    """Model for storing questions in the database.
    This model includes fields for question ID, text, course ID, creator user ID,
    and creation time. It is used to manage questions associated with courses within the application."""
    
    __tablename__ = 'questions'

    question_id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    answer_text = Column(String, nullable=False)  # Column for the answer to the question
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    course = relationship("CourseModel", back_populates="questions")
    creator = relationship("UserModel", back_populates="questions")
    