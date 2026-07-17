from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Boolean 
from datetime import datetime, timezone
from app.database import Base
from sqlalchemy.orm import relationship

class RoleModel(Base):
    """Model for storing user roles in the database.
    This model includes fields for role ID and role name.
    It is used to manage user roles within the application."""
    
    __tablename__ = 'roles'

    role_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    user_roles = relationship("UserRoleModel", back_populates="role")

class UserRoleModel(Base):
    """Model for storing user-role relationships in the database.
    This model includes fields for relation ID, user ID, and role ID.
    It is used to manage the roles assigned to users within the application."""
    
    __tablename__ = "user_roles"

    relation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    role_id = Column(Integer, ForeignKey("roles.role_id"))

    user = relationship("UserModel", back_populates="user_roles")
    role = relationship("RoleModel", back_populates="user_roles")

class UserModel(Base):
    """Model for storing user information in the database.
    This model includes fields for user ID, username, email, date of birth,
    password, role, full name, avatar, bio, joined date, and last login time.
    It is used to manage user accounts within the application."""
    
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    # username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    # date_of_birth = Column(Date, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    # bio = Column(String, nullable=True)
    joined = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_login = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=True)
    knowledge_assessment_last_shown_at = Column(DateTime(timezone=True), nullable=True)
    template_courses_initialized = Column(Boolean, default=False, nullable=False)

    user_roles = relationship("UserRoleModel", back_populates="user")
    course_progress = relationship("LearnerCourseProgressModel", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("DocumentModel", back_populates="uploaded_by_user")
    questions = relationship("QuestionModel", back_populates="creator")
    exam_submissions = relationship("ExamSubmissionModel", back_populates="user")
    chat_histories = relationship("ChatHistoryModel", back_populates="user")
    knowledge_assessment = relationship("KnowledgeAssessmentModel", back_populates="creator")
    recc_course = relationship("RecommendedCourseModel", back_populates="enroll_user")
