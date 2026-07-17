# backend/app/models/course_model.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, Text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.database import Base

class CourseModel(Base):
    """Model for storing course information in the database.
    This model includes fields for course ID, title, summary, creation time, and the user who created the course.
    It is used to manage courses within the application."""
    
    __tablename__ = "courses"

    course_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)  # Column for course summary
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    is_template = Column(Boolean, default=False, nullable=False)  # True for system template courses
    template_markdown = Column(Text, nullable=True)
    course_json = Column(JSONB, nullable=True)
        
    questions = relationship("QuestionModel", back_populates="course")
    learner_progress = relationship("LearnerCourseProgressModel", back_populates="course", cascade="all, delete-orphan")
    exams = relationship("ExamModel", back_populates="course")
    recc_course = relationship("RecommendedCourseModel", back_populates="course")
    images = relationship(
        "CourseImageModel",
        back_populates="course",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    quiz = relationship(
        "QuizModel",
        uselist=False,
        back_populates="course",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

class RecommendedCourseModel(Base):
    """Model for storing recommended courses for users in the database.
    This model includes fields for recommendation ID, user ID, course ID, reason for recommendation, score, and creation time.
    It is used to manage recommended course records within the application."""
    
    __tablename__ = "recommended_courses"

    recommendation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False, index=True)
    reason = Column(String, nullable=True)
    score = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # relationships
    course = relationship("CourseModel", back_populates="recc_course")
    enroll_user = relationship("UserModel", back_populates="recc_course")
