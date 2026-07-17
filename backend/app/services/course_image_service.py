import os
import logging
import uuid
from typing import List, Dict, Any
from pathlib import Path
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from app.models import CourseImageModel, CourseModel, LearnerCourseProgressModel

logger = logging.getLogger(__name__)

# Allowed image types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg", 
    "image/png",
    "image/gif",
    "image/webp",
    "image/svg+xml"
}

# Maximum file size: 10MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024

# Base directory for course images - aligned with other data paths
COURSE_IMAGES_BASE_DIR = os.getenv("COURSE_IMAGES_BASE_DIR", os.path.join(os.getcwd(), "data", "courses"))


def get_course_images_dir(course_id: int) -> str:
    """Get the directory path for a specific course's images."""
    return os.path.join(COURSE_IMAGES_BASE_DIR, str(course_id), "images")


def validate_image_file(file: UploadFile) -> None:
    """Validate image file type and size."""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )


async def verify_course_ownership(
    course_id: int,
    user_id: int,
    db: AsyncSession
) -> CourseModel:
    """Verify that the user owns the course."""
    try:
        result = await db.execute(
            select(CourseModel).where(
                and_(
                    CourseModel.course_id == course_id,
                    CourseModel.created_by == user_id
                )
            )
        )
        course = result.scalar_one_or_none()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course {course_id} not found or you don't have permission to access it."
            )
        
        return course
    except SQLAlchemyError as e:
        logger.error(f"Database error verifying course ownership: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


async def verify_course_access(
    course_id: int,
    user_id: int,
    db: AsyncSession
) -> CourseModel:
    """
    Verify that the user has access to the course.
    This includes both course owners (instructors) and enrolled learners.
    """
    try:
        # First check if user owns the course
        result = await db.execute(
            select(CourseModel).where(
                and_(
                    CourseModel.course_id == course_id,
                    CourseModel.created_by == user_id
                )
            )
        )
        course = result.scalar_one_or_none()
        
        if course:
            return course
        
        # If not the owner, check if the user is enrolled
        result = await db.execute(
            select(CourseModel).join(
                LearnerCourseProgressModel,
                and_(
                    LearnerCourseProgressModel.course_id == CourseModel.course_id,
                    LearnerCourseProgressModel.learner_user_id == user_id
                )
            ).where(CourseModel.course_id == course_id)
        )
        course = result.scalar_one_or_none()
        
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course {course_id} not found or you don't have access to it."
            )
        
        return course
    except SQLAlchemyError as e:
        logger.error(f"Database error verifying course access: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )


async def upload_course_image(
    course_id: int,
    user_id: int,
    file: UploadFile,
    db: AsyncSession
) -> Dict[str, Any]:
    """Upload an image for a course."""
    try:
        # Verify course ownership
        await verify_course_ownership(course_id, user_id, db)
        
        # Validate file
        validate_image_file(file)
        
        # Read file contents
        contents = await file.read()
        file_size = len(contents)
        
        if file_size > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {MAX_IMAGE_SIZE / (1024*1024)}MB"
            )
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        stored_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create directory if it doesn't exist
        images_dir = get_course_images_dir(course_id)
        os.makedirs(images_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(images_dir, stored_filename)
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Create database record
        image_record = CourseImageModel(
            course_id=course_id,
            filename=file.filename,
            stored_filename=stored_filename,
            file_path=file_path,
            content_type=file.content_type,
            file_size=file_size,
            uploaded_by=user_id
        )
        
        db.add(image_record)
        await db.commit()
        await db.refresh(image_record)
        
        logger.info(f"Image uploaded: {stored_filename} for course {course_id}")
        
        return {
            "image_id": image_record.image_id,
            "filename": image_record.filename,
            "stored_filename": image_record.stored_filename,
            "content_type": image_record.content_type,
            "file_size": image_record.file_size,
            "uploaded_at": image_record.uploaded_at.isoformat(),
            "url": f"/api/course/{course_id}/images/{stored_filename}"
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error uploading image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save image metadata"
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error uploading image: {e}")
        # Clean up file if it was created
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image"
        )


async def list_course_images(
    course_id: int,
    user_id: int,
    db: AsyncSession
) -> List[Dict[str, Any]]:
    """List all images for a course."""
    try:
        # Verify course ownership
        await verify_course_ownership(course_id, user_id, db)
        
        # Get all images for the course
        result = await db.execute(
            select(CourseImageModel)
            .where(CourseImageModel.course_id == course_id)
            .order_by(CourseImageModel.uploaded_at.desc())
        )
        
        images = result.scalars().all()
        
        return [
            {
                "image_id": img.image_id,
                "filename": img.filename,
                "stored_filename": img.stored_filename,
                "content_type": img.content_type,
                "file_size": img.file_size,
                "uploaded_at": img.uploaded_at.isoformat(),
                "url": f"/api/course/{course_id}/images/{img.stored_filename}"
            }
            for img in images
        ]
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error listing images: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve images"
        )


async def get_course_image_path(
    course_id: int,
    image_filename: str,
    user_id: int,
    db: AsyncSession
) -> tuple[str, str]:
    """Get the file path and content type for an image. Returns (file_path, content_type).
    Accepts either the original filename or stored_filename (UUID)."""
    try:
        # No access check - images are publicly viewable for all authenticated users
        # This allows learners to see course images before enrolling
        
        # Get image record - try both filename and stored_filename
        result = await db.execute(
            select(CourseImageModel).where(
                and_(
                    CourseImageModel.course_id == course_id,
                    or_(
                        CourseImageModel.filename == image_filename,
                        CourseImageModel.stored_filename == image_filename
                    )
                )
            )
        )
        
        image = result.scalar_one_or_none()
        
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        if not os.path.exists(image.file_path):
            logger.error(f"Image file not found on disk: {image.file_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image file not found on server"
            )
        
        return image.file_path, image.content_type
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve image"
        )


async def delete_course_image(
    course_id: int,
    stored_filename: str,
    user_id: int,
    db: AsyncSession
) -> Dict[str, str]:
    """Delete a course image."""
    try:
        # Verify course ownership
        await verify_course_ownership(course_id, user_id, db)
        
        # Get image record
        result = await db.execute(
            select(CourseImageModel).where(
                and_(
                    CourseImageModel.course_id == course_id,
                    CourseImageModel.stored_filename == stored_filename
                )
            )
        )
        
        image = result.scalar_one_or_none()
        
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        # Delete file from disk
        if os.path.exists(image.file_path):
            os.remove(image.file_path)
            logger.info(f"Deleted image file: {image.file_path}")
        
        # Delete database record
        await db.delete(image)
        await db.commit()
        
        logger.info(f"Deleted image: {stored_filename} from course {course_id}")
        
        return {"message": "Image deleted successfully"}
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error deleting image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete image"
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete image"
        )


async def delete_all_course_images(
    course_id: int,
    user_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """Delete all images for a course (used when deleting a course)."""
    try:
        # Verify course ownership
        await verify_course_ownership(course_id, user_id, db)
        
        # Get all images
        result = await db.execute(
            select(CourseImageModel).where(CourseImageModel.course_id == course_id)
        )
        
        images = result.scalars().all()
        
        deleted_count = 0
        for image in images:
            if os.path.exists(image.file_path):
                os.remove(image.file_path)
            await db.delete(image)
            deleted_count += 1
        
        await db.commit()
        
        # Clean up empty directory
        images_dir = get_course_images_dir(course_id)
        if os.path.exists(images_dir) and not os.listdir(images_dir):
            os.rmdir(images_dir)
        
        logger.info(f"Deleted {deleted_count} images for course {course_id}")
        
        return {
            "message": f"Deleted {deleted_count} images",
            "deleted_count": deleted_count
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Database error deleting course images: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete images"
        )
