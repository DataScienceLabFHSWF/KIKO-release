import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from datetime import datetime, timezone
from app.models import CourseModel, LearnerCourseProgressModel, QuestionModel
from .user_service import get_user_profile_by_email

logger = logging.getLogger(__name__)

async def get_instructor_statistics(
    email: str, 
    db: AsyncSession
) -> dict:
    """Fetch statistics for the instructor dashboard.
    This function retrieves the number of courses created by the instructor,
    the number of students enrolled in those courses, the number of questions asked by the instructor,
    and the number of questions asked by learners in the instructor's courses.
    It returns a dictionary containing these statistics along with the last activity timestamp."""
    
    try:
        user = await get_user_profile_by_email(email, db)

        instructor_id = user.user_id

        # Count courses created by instructor
        result = await db.execute(select(func.count()).select_from(CourseModel).where(CourseModel.created_by == instructor_id))
        courses_created = result.scalar_one()
        # Count students enrolled in instructor's courses
        result = await db.execute(
            select(
                func.count(
                    func.distinct(LearnerCourseProgressModel.learner_user_id)
                )
            )
            .select_from(LearnerCourseProgressModel)
            .join(CourseModel, CourseModel.course_id == LearnerCourseProgressModel.course_id)
            .where(CourseModel.created_by == instructor_id)
        )
        
        students = result.scalar_one()

        # Count questions asked by the instructor
        result = await db.execute(
            select(func.count()).select_from(QuestionModel).where(QuestionModel.created_by == instructor_id)
        )
        questions_asked = result.scalar_one()

        # Learner questions for instructor's courses
        result = await db.execute(select(func.count()).select_from(QuestionModel)
                                  .join(CourseModel, CourseModel.course_id == QuestionModel.course_id)
                                  .where(CourseModel.created_by == instructor_id)
                                  .where(QuestionModel.created_by != instructor_id)
                                )
        learner_questions = result.scalar_one()
        
        return {
            "students": students,
            "courses_created": courses_created,
            "questions_asked": questions_asked,
            "learner_questions": learner_questions,
            "last_activity": user.last_login.isoformat() if user.last_login else datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error during get learner statistics: {str(e)}"
        )
