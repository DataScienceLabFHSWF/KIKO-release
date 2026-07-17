import json, re
from typing import List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from app.models import CourseModel, RecommendedCourseModel
from app.core import PromptManager
from app.utils import lang_display
from .answer_grading_service import (get_ollama_client_and_model, generate_response, format_prompt)

RECOMMENDATION_COURSES_PROMPT_NAME = "recommendation_courses_prompt"

def _normalize(s: str) -> str:
    """Normalize a string for comparison: lowercase and strip."""

    return (s or "").strip().lower()

def _tokenize(s: str) -> List[str]:
    """Very simple tokenizer: extract alphanumeric tokens."""
    
    return re.findall(r"[a-zA-Z0-9\-]+", _normalize(s))

async def extract_topics_from_assessment(
    knowledge_assessment: str, 
    learning_path: str, 
    learning_step: str,
    prompt_manager: PromptManager,
    no_max_tokens: int,
    response_language: str
) -> List[str]:
    """
    Use LLM to extract 5-12 topics from the knowledge assessment + learning path + learning step.
    Fallback to naive keyword extraction if LLM fails to return valid JSON.
    """
    
    client, model_tag = get_ollama_client_and_model(None)
    
    blob = f"{knowledge_assessment}\n\n---\n{learning_path}\n\n---\n{learning_step}"
    
    # Load Knowledge assessment prompt template
    template = prompt_manager.load_prompt_template(RECOMMENDATION_COURSES_PROMPT_NAME, lang=response_language)

    # Format the prompt with the question, user_answer, reference_answer, and Grade summary
    recommendation_courses_prompt = format_prompt(
        template,
        blob=blob,
        language=lang_display(response_language)
    )
    
    print(f"ℹ️ recommendation_courses_prompt:\n {recommendation_courses_prompt}")
    
    text, tokens = generate_response(
        recommendation_courses_prompt, 
        client=client, 
        model_tag=model_tag,
        no_max_tokens=no_max_tokens)
    
    print(f"✅ Generated recommendation_courses_response:\n {text} and tokens used: {tokens}")
    
    # try strict JSON parse
    try:
        data = json.loads(text)
        topics = [t for t in data.get("topics", []) if isinstance(t, str)]
        return topics[:12]
    except Exception:
        # fallback: naive keywords from learning_path headings
        toks = _tokenize(learning_path + " " + knowledge_assessment)
        # very light filter
        uniq = []
        for t in toks:
            if len(t) < 4: 
                continue
            if t in uniq:
                continue
            uniq.append(t)
            if len(uniq) >= 12:
                break
        return uniq

def _score_course_against_topics(
    course: CourseModel, 
    topics: List[str]
) -> Tuple[float, str]:
    """
    Simple baseline: keyword overlap between topics and (title+summary).
    Returns (score, reason).
    """
    text = f"{course.title} {course.summary}"
    ctoks = set(_tokenize(text))
    ttoks = [_normalize(t) for t in topics]
    overlap = [t for t in ttoks if t in ctoks]
    # score = weighted overlap (can be improved later)
    score = len(overlap) / max(1, len(set(ttoks)))
    reason = f"Matched topics: {', '.join(overlap[:6])}" if overlap else "General fit based on course text."
    
    print(f"✅ Course '{course.title}' scored {score} with reason: {reason}")
    
    return score, reason

async def refresh_recommendations_for_user(
    user_id: int,
    knowledge_assessment: str,
    learning_path: str,
    learning_step: str,
    db: AsyncSession,
    prompt_manager: PromptManager,
    no_max_tokens: int,
    response_language: str,
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """
    Refresh recommended courses for a user based on their knowledge assessment, learning path, and learning step.
    Returns a list of recommended courses with details.
    """
    try:
        # 1) extract topics
        topics = await extract_topics_from_assessment(
            knowledge_assessment, 
            learning_path, 
            learning_step,
            prompt_manager,
            no_max_tokens,
            response_language
        )
        
        if not topics:
            # If nothing extracted, clear and return empty
            await db.execute(
                delete(RecommendedCourseModel)
                .where(RecommendedCourseModel.user_id == user_id)
            )

            await db.commit()
            return []
        
        print(f"✅ Extracted topics for user {user_id}: {topics}")

        # 2) fetch all courses (optionally exclude already enrolled in your query)
        res = await db.execute(select(CourseModel))
        
        courses = res.scalars().all()
        
        print(f"✅ Fetched {len(courses)} courses for recommendation scoring.")

        # 3) score and pick top-k
        scored: List[Tuple[CourseModel, float, str]] = []
        
        for c in courses:
            sc, reason = _score_course_against_topics(c, topics)
            if sc > 0:
                scored.append((c, sc, reason))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:top_k]

        print(f"✅ Top {len(top)} courses selected for user {user_id}.")

        # 4) persist recommendations (upsert-ish)
        # clear previous recs for user first (simple)
        await db.execute(
            delete(RecommendedCourseModel)
            .where(RecommendedCourseModel.user_id == user_id)
        )
        
        for c, sc, reason in top:
            db.add(
                RecommendedCourseModel(user_id=user_id, course_id=c.course_id, score=float(sc), reason=reason)
            )
        
        await db.commit()
        
        response = [
            {
                "course_id": c.course_id, 
                "title": c.title, 
                "summary": c.summary, 
                "reason": r, 
                "score": sc
            } 
            for c, sc, r in top
        ]

        print(f"✅ Persisted top {len(response)} recommendations for user {user_id}.")
        
        return response
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"refresh_recommendations_for_user: {str(e)}"
        )
