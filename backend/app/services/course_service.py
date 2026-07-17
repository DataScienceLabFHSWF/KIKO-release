from typing import Any, Dict, List, Optional
from sqlalchemy import select, delete, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from app.models import (
    CourseModel, QuestionModel, LearnerCourseProgressModel,
    ExamModel, ExamQuestionModel, ExamSubmissionModel,
    ExamAnswerModel
)

async def list_user_courses(
    user_id: int, 
    db: AsyncSession
) -> List[Dict[str, Any]]:
    """
    Returns all courses created by this instructor with question counts.
    """
    try:
        result = await db.execute(
            select(CourseModel)
            .where(CourseModel.created_by == user_id)
        )

        courses: List[CourseModel] = result.scalars().all()

        if not courses:
            return []

        counts_result = await db.execute(
            select(QuestionModel.course_id, func.count())
            .select_from(QuestionModel)
            .where(QuestionModel.course_id.in_([c.course_id for c in courses]))
            .group_by(QuestionModel.course_id)
        )

        counts_map = {cid: cnt for cid, cnt in counts_result.all()}

        return [
            {
                "course_id": c.course_id,
                "title": c.title,
                "summary": c.summary,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "question_count": counts_map.get(c.course_id, 0),
            }
            for c in courses
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error during listing all courses from DB for the user {user_id}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during listing all courses from DB for the user {user_id}: {str(e)}"
        )

async def get_course_detail_by_id(
    course_id: int, 
    user_id: int, 
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Returns a single course (must be owned by instructor) including its questions.
    """
    try:
        result = await db.execute(
            select(CourseModel)
            .options(joinedload(CourseModel.questions))
            .where(CourseModel.course_id == course_id)
        )

        course: Optional[CourseModel] = result.scalars().first()

        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ Course not found")
        
        if course.created_by != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="❌ Forbidden")

        return {
            "course": {
                "course_id": course.course_id,
                "title": course.title,
                "summary": course.summary,
                "created_at": course.created_at.isoformat() if course.created_at else None,
            },
            "questions": [
                {
                    "question_id": q.question_id,
                    "text": q.text,
                    "answer_text": q.answer_text,
                }
                for q in (course.questions or [])
            ],
        }
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error during course {course_id} details from DB for the user {user_id}: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during course {course_id} details from DB for the user {user_id}: {str(e)}"
        )

async def update_course_by_id(
    course_id: int,
    user_id: int,
    payload: Dict[str, Any],
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Update title & summary; optionally replace all questions with payload['questions'].
    """
    try:
        result = await db.execute(
            select(CourseModel)
            .where(CourseModel.course_id == course_id)
        )
        
        course: Optional[CourseModel] = result.scalars().first()
        
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ Course not found")
        
        if course.created_by != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="❌ Forbidden")

        title = payload.get("title")
        summary = payload.get("summary")
        questions = payload.get("questions")  # optional list of {text, answer_text}

        if isinstance(title, str) and title.strip():
            course.title = title.strip()
        if isinstance(summary, str) and summary.strip():
            course.summary = summary.strip()

        if questions is not None:
            # Replace all questions atomically
            await db.execute(
                delete(QuestionModel)
                .where(QuestionModel.course_id == course.course_id)
            )
            
            if isinstance(questions, list):
                for q in questions:
                    text = (q or {}).get("text", "").strip()
                    ans = (q or {}).get("answer_text", "").strip()
                    if not text or not ans:
                        continue
                    db.add(
                        QuestionModel(
                            text=text,
                            answer_text=ans,
                            course_id=course.course_id,
                            created_by=user_id,
                        )
                    )

        await db.commit()
        
        return {"message": "updated", "course_id": course.course_id}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error during updating course {course_id} from DB for the user {user_id}: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during updating course {course_id} from DB for the user {user_id}: {str(e)}"
        )

async def delete_course_by_id(
    course_id: int,
    user_id: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """
    Delete a course owned by instructor and all dependent records to avoid FK conflicts.
    """
    try:
        result = await db.execute(
            select(CourseModel)
            .where(CourseModel.course_id == course_id)
        )
        
        course: Optional[CourseModel] = result.scalars().first()
        
        if not course:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ Course not found")
        
        if course.created_by != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="❌ Forbidden")

        # Exams & dependents
        exam_ids_res = await db.execute(
            select(ExamModel.exam_id)
            .where(ExamModel.course_id == course.course_id)
        )
        
        exam_ids = [eid for (eid,) in exam_ids_res.all()]
        
        if exam_ids:
            # Delete exam answers by submissions
            sub_ids_res = await db.execute(
                select(ExamSubmissionModel.submission_id)
                .where(ExamSubmissionModel.exam_id.in_(exam_ids))
            )

            sub_ids = [sid for (sid,) in sub_ids_res.all()]
            
            if sub_ids:
                await db.execute(
                    delete(ExamAnswerModel)
                    .where(ExamAnswerModel.submission_id.in_(sub_ids))
                )

            # Delete exam answers by questions
            q_ids_res = await db.execute(
                select(ExamQuestionModel.question_id)
                .where(ExamQuestionModel.exam_id.in_(exam_ids))
            )
            q_ids = [qid for (qid,) in q_ids_res.all()]
            
            if q_ids:
                await db.execute(
                    delete(ExamAnswerModel)
                    .where(ExamAnswerModel.question_id.in_(q_ids))
                )
            
            # Delete submissions, questions, exams
            await db.execute(
                delete(ExamSubmissionModel)
                .where(ExamSubmissionModel.exam_id.in_(exam_ids))
            )

            await db.execute(
                delete(ExamQuestionModel)
                .where(ExamQuestionModel.exam_id.in_(exam_ids))
            )

            await db.execute(
                delete(ExamModel)
                .where(ExamModel.exam_id.in_(exam_ids))
            )
        
        # Enrollments
        await db.execute(
            delete(LearnerCourseProgressModel)
            .where(LearnerCourseProgressModel.course_id == course.course_id)
        )
        
        # Questions
        await db.execute(
            delete(QuestionModel)
            .where(QuestionModel.course_id == course.course_id)
        )
        
        # Course
        await db.execute(
            delete(CourseModel)
            .where(CourseModel.course_id == course.course_id)
        )
        
        await db.commit()
        return {"message": "deleted", "course_id": course_id}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error during deleting course {course_id} from DB for the user {user_id}: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during deleting course {course_id} from DB for the user {user_id}: {str(e)}"
        )
