from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app.database import Base

class CourseImageModel(Base):
    """Model for storing course image metadata in the database.
    This model tracks images uploaded for courses, including file path, size, and content type.
    Images are stored on the file system and this model maintains the metadata and references."""
    
    __tablename__ = "course_images"

    image_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.course_id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String, nullable=False)  # Original filename
    stored_filename = Column(String, nullable=False, unique=True)  # Unique filename on disk
    file_path = Column(String, nullable=False)  # Full path to the image file
    content_type = Column(String, nullable=False)  # MIME type (image/png, image/jpeg, etc.)
    file_size = Column(BigInteger, nullable=False)  # Size in bytes
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    # Relationships
    course = relationship("CourseModel", back_populates="images")
    uploader = relationship("UserModel")
