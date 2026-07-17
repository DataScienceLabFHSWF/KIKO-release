from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Float, Boolean
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base

class KnowledgeAssessmentModel(Base):
    """Model for storing knowledge assessment questions in the database.
    This model includes fields for question ID, topic, question text, type, correct answer,
    creator, and creation time. It is used to manage knowledge assessment questions within the application."""
    
    __tablename__ = 'knowledge_assessment'
    
    question_id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    question = Column(String, nullable=False)
    type = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)  # Column for the answer to the question
    created_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    creator = relationship("UserModel", back_populates="knowledge_assessment")

class KnowledgeAssessmentAttemptModel(Base):
    """Model for storing knowledge assessment attempts in the database.
    This model includes fields for attempt ID, user ID, start time, finish time, and score percentage.
    It is used to manage user attempts at knowledge assessments within the application."""
    
    __tablename__ = "knowledge_assessment_attempts"
    
    attempt_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    score_percent = Column(Float, nullable=True)
    
    answers = relationship("KnowledgeAssessmentAnswerModel", back_populates="attempt")

class KnowledgeAssessmentAnswerModel(Base):
    """Model for storing knowledge assessment answers in the database.
    This model includes fields for answer ID, attempt ID, question ID, user answer,
    and correctness status. It is used to manage answers submitted by users for knowledge assessments within the application."""
    
    __tablename__ = "knowledge_assessment_answers"
    
    answer_id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("knowledge_assessment_attempts.attempt_id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("knowledge_assessment.question_id"), nullable=False)
    user_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    
    attempt = relationship("KnowledgeAssessmentAttemptModel", back_populates="answers")

class KnowledgeAssessmentConfigModel(Base):
    """Model for storing knowledge assessment configuration in the database.
    This model includes fields for config ID, enabled status, size, question IDs,
    and the last update time. It is used to manage configuration settings for knowledge assessments within the application."""
    
    __tablename__ = "knowledge_assessment_config"

    config_id = Column(Integer, primary_key=True, index=True)
    enabled = Column(Boolean, nullable=False, default=True)
    size = Column(Integer, nullable=False, default=5)
    question_ids = Column(JSONB, nullable=False, default=list)  # list[int]
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
