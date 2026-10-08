# backend/app/api/routes/chatbot.py

import logging, json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import (
    require_role, run_query, get_user_profile_by_email, save_chat_turn,
    fetch_chat_history, clear_chat_history, get_request_lang
)
from app.schemas import (
    ChatQueryRequest, COMMON_ERROR_RESPONSES, ChatAnswerResponse, 
    ChatHistoryResponse, ChatMessageResponse, ChatQueryResponse
)
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(responses=COMMON_ERROR_RESPONSES)

@router.post(
    "/query", 
    response_model=ChatQueryResponse,
    operation_id="submit_chat_query"
)
async def query_chatbot(
    payload: ChatQueryRequest,
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db)
) -> ChatQueryResponse:
    """Endpoint to query the chatbot with a question and get an answer."""
    try:
        logger.info(f"ℹ️ query API: Received query from USER : {user['email']} and language: {response_language}")

        email_address = user["email"]
        
        user_profile = await get_user_profile_by_email(email_address, db)
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="❌ User not found"
            )
        
        response = await run_query(
            query=payload.query,
            embedding_model=payload.embedding_model,
            llm_model=payload.llm_model,
            response_language=response_language,
            user_id=user_profile.user_id,
            user_role=user_profile.role,
            db=db           
        )

        if response is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "❌ No relevant documents found. Cannot provide an answer."
                    if response_language == "en"
                    else "❌ Keine relevanten Dokumente gefunden. Kann keine Antwort geben."
                )
            )
        
        logger.info(f"✅ query LLM answer: {response}.")

        # 🔐 persist this Q&A turn
        await save_chat_turn(
            user_id=user_profile.user_id,
            role=user_profile.role,
            user_query=payload.query,
            assistant_payload=response,
            db=db,
        )
        
        result = ChatQueryResponse(
            data=ChatAnswerResponse.model_validate(response)
        )

        logger.info(f"✅ query API: Responding with result: {result}.")

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error processing chat query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )

@router.get(
    "/chat/history", 
    response_model=ChatHistoryResponse,
    operation_id="get_chat_history"
)
async def chat_history(
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    db: AsyncSession = Depends(get_db)
) -> ChatHistoryResponse:
    """Endpoint to retrieve chat history for the authenticated user."""
    try:
        logger.info(f"ℹ️ chat/history API: Fetching chat history for USER : {user['email']}")

        email = user["email"]

        user_profile = await get_user_profile_by_email(email, db)

        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="❌ User not found"
            )
        
        # fetch chat history rows
        rows = await fetch_chat_history(user_profile.user_id, db=db)
        
        messages: list[ChatMessageResponse] = []
        
        # normalize to FE format (user/assistant messages list)
        for row in rows:
            # one row == one turn
            
            # user message
            messages.append(
                ChatMessageResponse(
                    role="user",
                    content=row.user_query,
                    timestamp=row.timestamp.isoformat() if row.timestamp else None,
                    sources=[]  # user message doesn't have sources
                )
            )
            
            # assistant message
            try:
                payload = json.loads(row.assistant_response)
                
                if isinstance(payload, dict) and "data" in payload:
                    content = payload.get("data", {}).get("answer", row.assistant_response)
                    sources = payload.get("data", {}).get("source_docs", [])
                elif isinstance(payload, dict):
                    content = payload.get("answer", row.assistant_response)
                    sources = payload.get("source_docs", [])
                else:
                    content, sources = row.assistant_response, []
            except Exception:
                content, sources = row.assistant_response, []
            
            messages.append(
                ChatMessageResponse(
                    role="assistant",
                    content=content,
                    sources=sources,
                    timestamp=row.timestamp.isoformat() if row.timestamp else None
                )
            )
        
        response = ChatHistoryResponse(messages=messages)

        logger.info(f"✅ chat/history API: Retrieved {response}")
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error fetching chat history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )

@router.delete(
    "/history",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_chat_history"
)
async def delete_chat_history(
    user = Depends(require_role(["Learner", "Instructor", "Admin"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete ALL chat messages for the authenticated user.
    Returns 204 No Content on success.
    """
    try:
        logger.info(f"ℹ️ delete history API: Deleting chat history for USER : {user['email']}")
        
        user_profile = await get_user_profile_by_email(user["email"], db)
        
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="❌ User not found"
            )
        
        await clear_chat_history(user_profile.user_id, db)
        
        logger.info(f"✅ delete history API: Chat history deleted for USER : {user['email']}")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ Error deleting chat history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )
