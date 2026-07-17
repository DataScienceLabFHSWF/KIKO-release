from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, String, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base
from sqlalchemy.orm import relationship

class LearnerCourseProgressModel(Base):
    __tablename__ = "learner_course_progress"

    progress_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False, index=True)
    learner_user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)

    current_nav = Column(String, nullable=True)
    current_module_id = Column(String, nullable=True)
    completion_percent = Column(Float, nullable=False, default=0.0)

    progress_json = Column(JSONB, nullable=False, default=dict)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("course_id", "learner_user_id", name="uq_learner_course_progress"),
    )
    
    user = relationship("UserModel", back_populates="course_progress")
    course = relationship("CourseModel", back_populates="learner_progress")

class LearnerQuizAttemptModel(Base):
    __tablename__ = "learner_quiz_attempts"

    attempt_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False, index=True)
    learner_user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)

    module_id = Column(String, nullable=True)
    assessment_id = Column(String, nullable=False, index=True)
    assessment_type = Column(String, nullable=False)  # module_quiz | final_quiz

    submitted_answers_json = Column(JSONB, nullable=False, default=list)
    feedback_json = Column(JSONB, nullable=False, default=list)

    score = Column(Float, nullable=False, default=0.0)
    total_points = Column(Float, nullable=False, default=0.0)
    percent = Column(Float, nullable=False, default=0.0)
    passed = Column(Boolean, nullable=False, default=False)
    german_grade = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
