from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class ExamModel(Base):
    """Model for storing exam information in the database.
    This model includes fields for exam ID, course ID, title, description, and scheduled time.
    It is used to manage exams associated with courses within the application."""
    
    __tablename__ = "exams"

    exam_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)

    course = relationship("CourseModel", back_populates="exams")
    questions = relationship("ExamQuestionModel", back_populates="exam")
    submissions = relationship("ExamSubmissionModel", back_populates="exam")

class ExamQuestionModel(Base):
    """Model for storing exam questions in the database.
    This model includes fields for question ID, exam ID, question text, correct answer,
    and creation time. It is used to manage questions associated with exams within the application."""
    
    __tablename__ = "exam_questions"

    question_id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.exam_id"), nullable=False)
    text = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    exam = relationship("ExamModel", back_populates="questions")
    answers = relationship("ExamAnswerModel", back_populates="question")

class ExamAnswerModel(Base):
    """Model for storing exam answers in the database.
    This model includes fields for answer ID, submission ID, question ID, and the answer text
    It is used to manage answers submitted by users for exam questions within the application."""
    
    __tablename__ = "exam_answers"

    answer_id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("exam_submissions.submission_id"), nullable=False)
    question_id = Column(Integer, ForeignKey("exam_questions.question_id"), nullable=False)
    answer_text = Column(String, nullable=False)

    submission = relationship("ExamSubmissionModel", back_populates="answers")
    question = relationship("ExamQuestionModel", back_populates="answers")

class ExamSubmissionModel(Base):
    """Model for storing exam submissions in the database.
    This model includes fields for submission ID, exam ID, user ID, pass status,
    and submission time. It is used to manage user submissions for exams within the application."""
    
    __tablename__ = "exam_submissions"

    submission_id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.exam_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    passed = Column(Integer, nullable=True)
    submitted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    exam = relationship("ExamModel", back_populates="submissions")
    user = relationship("UserModel", back_populates="exam_submissions")
    answers = relationship("ExamAnswerModel", back_populates="submission")
