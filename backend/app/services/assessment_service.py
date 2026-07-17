# backend/app/services/assessment_service.py
import logging, random, asyncio, json
from sqlalchemy import select, delete
from typing import List, Dict, Any, Tuple
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.schemas import (AssessmentQuestion, AssessmentPayload, AssessmentResult,
                         GradedAnswer)
from app.models import (KnowledgeAssessmentModel, KnowledgeAssessmentConfigModel)
from app.core import PromptManager
from .answer_grading_service import (grade_user_answer, get_ollama_client_and_model, generate_response,
                                     format_prompt)
from .configuration_service import get_app_config_and_libary_available
from .recommendation_service import refresh_recommendations_for_user
from app.utils import lang_display

logger = logging.getLogger(__name__)
KNOW_ASSESS_PROMPT_NAME = "knowledge_assessment_prompt"
LEARNING_PATH_PROMPT_NAME = "learning_path_prompt"
LEARNING_STEP_PROMPT_NAME = "learning_step_prompt"

def _val(obj, key, default=None):
    """Helper to get attribute or dict key with default."""
    if hasattr(obj, key):
        return getattr(obj, key)
    if isinstance(obj, dict):
        return obj.get(key, default)
    return default

def _build_questions_json_from_graded(
    graded_answers: List[Any],
    original_answers: List[Dict[str, Any]],
    q_map: Dict[int, Any],
) -> Dict[str, Any]:
    """Build the questions JSON structure for prompts from graded answers."""

    by_qid_user_ans = {
        a["question_id"]: (a.get("user_answer") or "").strip()
        for a in original_answers
        if isinstance(a, dict) and "question_id" in a
    }
    
    items = []
    for ga in graded_answers:
        qid = _val(ga, "question_id")
        
        if qid is None:
            continue
        
        q_obj = q_map.get(qid)

        if not q_obj:
            continue
        
        items.append(
            {
                "question": getattr(q_obj, "question", None),
                "user_answer": by_qid_user_ans.get(qid, None),
                "reference_answer": getattr(q_obj, "correct_answer", None),
                "grade": _val(ga, "grade", 6),
                "summary": _val(ga, "summary", None),
            }
        )

    response = {"questions": items}

    print(f"✅ Built questions JSON for prompts: {response}")

    return response

def _localize_graded_json_for_prompt(graded_json: Dict[str, Any]) -> Dict[str, Any]:
    """Localize the graded JSON structure for prompts based on language."""
    
    items = []
    
    for it in graded_json.get("questions", []):
        items.append(
            {
                "frage": it.get("question"),
                "benutzerantwort": it.get("user_answer"),
                "referenzantwort": it.get("reference_answer"),
                "note": it.get("grade"),
                "begründung": it.get("summary"),
            }
        )
    
    response = {"fragen": items}
    print(f"✅ Localized graded JSON for prompt: {response}")
    return response

def generate_knowledge_assessment_from_graded(
    graded_json: Dict[str, Any],
    prompt_manager: PromptManager,
    no_max_tokens: int,
    response_language: str
) -> Tuple[str, int]:
    """
    Produce a **knowledge assessment** using the graded data.
    """
    client, model_tag = get_ollama_client_and_model(None)

    # 'de' → German keys, 'en' → unchanged
    if response_language == "de":
        prompt_json = _localize_graded_json_for_prompt(graded_json) 
        json_data_str = json.dumps(prompt_json, ensure_ascii=False, indent=4)
    else:
        json_data_str = json.dumps(graded_json, indent=4)
    
    # Load Knowledge assessment prompt template
    template = prompt_manager.load_prompt_template(KNOW_ASSESS_PROMPT_NAME, lang=response_language)

    # Format the prompt with the question, user_answer, reference_answer, and Grade summary
    knowledge_assessment_prompt = format_prompt(
        template, 
        json_data=json_data_str,
        language=lang_display(response_language)
    )

    print(f"ℹ️ knowledge_assessment_prompt:\n {knowledge_assessment_prompt}")
    
    text, tokens = generate_response(knowledge_assessment_prompt, client, model_tag, no_max_tokens)

    print(f"✅ Generated Knowledge Assessment:\n{text} and tokens used: {tokens}")

    return text, tokens

def generate_learning_path_from_graded(
    graded_json: Dict[str, Any],
    knowledge_assessment_text: str,
    prompt_manager: PromptManager,
    no_max_tokens: int,
    response_language: str
) -> Tuple[str, int]:
    """
    Produce a **personalized learning path** using the knowledge assessment + graded data.
    """
    client, model_tag = get_ollama_client_and_model(None)
    
    # 'de' → German keys, 'en' → unchanged
    if response_language == "de":
        prompt_json = _localize_graded_json_for_prompt(graded_json)
        json_data_str = json.dumps(prompt_json, ensure_ascii=False, indent=4)
    else:
        json_data_str = json.dumps(graded_json, indent=4)
    
    # Load Learning path prompt template
    template = prompt_manager.load_prompt_template(LEARNING_PATH_PROMPT_NAME, lang=response_language)

    # Format the prompt with the question, user_answer, reference_answer, Grade summary and knowledge_assessment
    learning_path_prompt = format_prompt(
        template, 
        json_data=json_data_str,
        knowledge_assessment=knowledge_assessment_text,
        language=lang_display(response_language)
    )

    print(f"ℹ️ learning_path_prompt:\n {learning_path_prompt}")
    
    text, tokens = generate_response(learning_path_prompt, client, model_tag, no_max_tokens)

    print(f"✅ Generated Learning Path:\n{text} and tokens used: {tokens}")

    return text, tokens

def generate_learning_step_from_path(
    learning_path_text: str,
    prompt_manager: PromptManager,
    no_max_tokens: int,
    response_language: str
) -> Tuple[str, int]:
    """
    Produce a **first learning step** explanation derived from the learning path (focus on weak/grade=3 areas).
    """
    client, model_tag = get_ollama_client_and_model(None)

    # Load Learning step prompt template
    template = prompt_manager.load_prompt_template(LEARNING_STEP_PROMPT_NAME, lang=response_language)

    # Format the prompt with learning_path
    learning_step_prompt = format_prompt(
        template, 
        learning_path=learning_path_text,
        language=lang_display(response_language)
    )
    
    print(f"ℹ️ learning_step_prompt:\n {learning_step_prompt}")
    
    text, tokens = generate_response(learning_step_prompt, client, model_tag, no_max_tokens)

    print(f"✅ Generated Learning Step Explanation:\n{text}")

    return text, tokens

async def get_assessment_quiz_for_user(db: AsyncSession) -> List[AssessmentQuestion]:
    """Fetch a random quiz for the user based on admin config."""
    try:
        # 1) Load (or default) admin config
        cfg_res = await db.execute(select(KnowledgeAssessmentConfigModel))

        cfg = cfg_res.scalars().first()

        if not cfg:
            # default behavior if admin didn't configure yet
            enabled, size, ids = True, 5, []
        else:
            enabled, size, ids = cfg.enabled, int(cfg.size or 5), list(cfg.question_ids or [])

        if not enabled:
            return []  # knowledge check disabled

        # 2) Fetch candidate questions
        if ids:  # admin selected a pool
            q_res = await db.execute(
                select(KnowledgeAssessmentModel)
                .where(KnowledgeAssessmentModel.question_id.in_(ids))
            )
            candidates = q_res.scalars().all()
            # keep only the subset that still exists in DB
            # (ids could be stale if a question was deleted)
        else:
            # fallback: whole table (ordered newest first)
            q_res = await db.execute(
                select(KnowledgeAssessmentModel)
                .order_by(KnowledgeAssessmentModel.created_at.desc())
            )
            candidates = q_res.scalars().all()

        if not candidates:
            return []

        # 3) Sample by configured size
        k = min(size, len(candidates))
        picked = random.sample(candidates, k=k)

        # 4) Shape response
        return [
            AssessmentQuestion(
                question_id=q.question_id,
                topic=q.topic,
                question=q.question,
                type=q.type,
            )
            for q in picked
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"quiz_fetch_failed: {str(e)}"
        )

async def submit_assessment_quiz_for_user(
    payload: AssessmentPayload, 
    user_id: int, 
    db: AsyncSession,
    response_language: str
) -> AssessmentResult:
    """Submit user answers, grade them, generate knowledge assessment, learning path, learning step, and recommendations."""

    try:
        print(f"ℹ️ Submitting the user answers: {payload}")

        if not payload.answers or len(payload.answers) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"❌ validation_error: {str(e)}")
        
        q_ids = [a['question_id'] for a in payload.answers]

        # Fetch questions from DB
        result = await db.execute(
            select(KnowledgeAssessmentModel)
            .where(KnowledgeAssessmentModel.question_id.in_(q_ids))
        )

        questions = result.scalars().all()
        
        if not questions:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ invalid_questions: none found")
        
        q_map = {q.question_id: q for q in questions}

        print(f"ℹ️ q_ids: {q_ids} and q_map: {q_map} and answers: {payload.answers}")
        
        # Build grading tasks (one per answer)
        tasks = []
        normalized_answers = []  # keep order aligned with tasks
        
        for a in payload.answers:
            q = q_map.get(a["question_id"])
            
            if not q:
                # skip unknown question ids silently or raise
                continue
            
            ua = (a["user_answer"] or "").strip()

            normalized_answers.append(
                (
                    q.question_id, 
                    q.question,
                    ua,
                    q.correct_answer
                )
            )

            tasks.append(
                grade_user_answer(
                    question=q.question,
                    user_answer=ua,
                    inference_model_name=None,
                    reference_answer=q.correct_answer,
                    no_max_tokens=1024,
                    response_language=response_language
                )
            )

        if not tasks:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="❌ No valid answers to grade.")

        # Run all grading calls concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Shape response
        graded_answers : List[GradedAnswer] = []

        for (qid, _qtext, _ua, _ref), ai in zip(normalized_answers, results):
            if isinstance(ai, Exception):
                graded_answers.append(GradedAnswer(
                    question_id=qid,
                    grade=6,
                    summary=None,
                ))
            else:
                graded_answers.append(GradedAnswer(
                    question_id=qid,
                    grade=ai.get("grade", 6),
                    summary=ai.get("summary", None),
                ))

        print(f"✅ Graded answers: {graded_answers} and q_map: {q_map}")

        # Build graded JSON for prompts
        graded_json = _build_questions_json_from_graded(
            graded_answers=graded_answers,
            original_answers=payload.answers,
            q_map=q_map,
        )
        
        configs = await get_app_config_and_libary_available()
        
        prompt_mgr = PromptManager(configs)
        
        knowledge_text, _ = generate_knowledge_assessment_from_graded(graded_json, prompt_mgr, 2048, response_language)
        learning_path_text, _ = generate_learning_path_from_graded(graded_json, knowledge_text, prompt_mgr, 2048, response_language)
        learning_step_text, _ = generate_learning_step_from_path(learning_path_text, prompt_mgr, 2048, response_language)
        
        recommendations = await refresh_recommendations_for_user(
            user_id=user_id,
            knowledge_assessment=knowledge_text,
            learning_path=learning_path_text,
            learning_step=learning_step_text,
            db=db,
            prompt_manager=prompt_mgr,
            no_max_tokens=2048,
            response_language=response_language
        )
        
        response = AssessmentResult(
            graded_answers=graded_answers,
            knowledge_assessment=knowledge_text,
            learning_path=learning_path_text,
            learning_step=learning_step_text,
            recommended_courses=recommendations
        )
        
        print(f"✅ Assessment and Recommendation pipeline done: {response}")
        
        return response
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"❌ Database error: {str(e)}")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"❌ quiz_submit_failed: {str(e)}")

async def list_all_questions(db: AsyncSession) -> List[Dict[str, Any]]:
    """List all knowledge assessment questions in the system."""

    try:
        res = await db.execute(
            select(KnowledgeAssessmentModel)
            .order_by(KnowledgeAssessmentModel.created_at.desc())
        )
        
        rows = res.scalars().all()
        
        return [
            {
                "question_id": q.question_id,
                "topic": q.topic,
                "question": q.question,
                "type": q.type,
                "created_by": q.created_by,
            }
            for q in rows
        ]
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"❌ Failed to list_all_questions : {str(e)}"
        )

async def fetch_config(db: AsyncSession) -> Dict[str, Any]:
    """Fetch the knowledge assessment configuration (or default)."""

    try:
        res = await db.execute(select(KnowledgeAssessmentConfigModel))
        
        cfg = res.scalars().first()
        
        if not cfg:
            # default on first run
            cfg = KnowledgeAssessmentConfigModel(enabled=True, size=5, question_ids=[])
            db.add(cfg)
            await db.commit()
            await db.refresh(cfg)
        
        return {"enabled": cfg.enabled, "size": cfg.size, "question_ids": cfg.question_ids}
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"❌ Failed to fetch_config : {str(e)}"
        )

async def update_config(
    payload: Dict[str, Any], 
    db: AsyncSession
) -> None:
    """Update the knowledge assessment configuration."""
    
    try:
        enabled = bool(payload.get("enabled", True))
        size = int(payload.get("size", 5))
        question_ids = list(payload.get("question_ids", []))
        
        if size < 1:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="❌ size must be >= 1")
        
        # validate IDs exist
        if question_ids:
            res = await db.execute(
                select(KnowledgeAssessmentModel.question_id)
                .where(KnowledgeAssessmentModel.question_id.in_(question_ids))
            )
            
            existing = {x for (x,) in res.all()}  # tuples
            missing = set(question_ids) - existing
            if missing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"❌ Unknown question IDs: {sorted(missing)}")
        
        res = await db.execute(select(KnowledgeAssessmentConfigModel))
        
        cfg = res.scalars().first()
        
        if not cfg:
            cfg = KnowledgeAssessmentConfigModel()
            db.add(cfg)
        
        cfg.enabled = enabled
        cfg.size = size
        cfg.question_ids = question_ids
        cfg.updated_at = datetime.now(timezone.utc)
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"❌ Failed to update_config : {str(e)}"
        )

async def remove_question(
    question_id: int, 
    db: AsyncSession
) -> None:
    """Remove a knowledge assessment question by ID, and clean up config if needed."""

    try:
        # optional delete API
        
        await db.execute(
            delete(KnowledgeAssessmentModel)
            .where(KnowledgeAssessmentModel.question_id == question_id)
        )
        
        await db.commit()
        
        # also remove from config if present
        res = await db.execute(select(KnowledgeAssessmentConfigModel))
        cfg = res.scalars().first()
        
        if cfg and cfg.question_ids and question_id in cfg.question_ids:
            cfg.question_ids = [i for i in cfg.question_ids if i != question_id]
            await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"❌ Failed to remove_question : {str(e)}"
        )
