# API for QAChainManager
import logging, json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.services import (require_role, run_query, get_user_profile_by_email,
                          save_chat_turn, fetch_chat_history, clear_chat_history,
                          get_request_lang)
from app.schemas import ChatQueryRequest
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/query")
async def query_chatbot(
    payload: ChatQueryRequest,
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    response_language: str = Depends(get_request_lang),
    db: AsyncSession = Depends(get_db)
):
    """Endpoint to query the chatbot with a question and get an answer."""
    try:
        print(f"ℹ️ query API: Received query from USER : {user['email']} and language: {response_language}")

        email_address = user["email"]
        
        user_profile = await get_user_profile_by_email(email_address, db)
        
        if not user_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")
        
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
        
        # 🔐 persist this Q&A turn
        await save_chat_turn(
            user_id=user_profile.user_id,
            role=user_profile.role,
            user_query=payload.query,
            assistant_payload=response,
            db=db,
        )

        print(f"✅ query API: Responding to USER : {user['email']} with answer.")

        return JSONResponse(status_code=status.HTTP_200_OK, content={"data": response})
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ chatbot/query error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/chat/history")
async def chat_history(
    user=Depends(require_role(["Learner", "Instructor", "Admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Endpoint to retrieve chat history for the authenticated user."""
    try:
        print(f"ℹ️ chat/history API: Fetching chat history for USER : {user['email']}")

        email = user["email"]

        user_profile = await get_user_profile_by_email(email, db)

        if not user_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")
        
        # fetch chat history rows
        rows = await fetch_chat_history(user_profile.user_id, db=db)

        print(f"ℹ️ chat/history API: Fetched {rows}")
        
        messages = []
        
        if not rows:
            return JSONResponse(status_code=status.HTTP_200_OK, content={"messages": messages})
        
        # normalize to FE format (user/assistant messages list)
        for row in rows:
            # one row == one turn
            
            # user message
            messages.append({
                "role": "user",
                "content": row.user_query,
                "timestamp": row.timestamp.isoformat(),
            })
            
            # assistant message
            try:
                payload = json.loads(row.assistant_response)
                content = payload.get("answer", row.assistant_response)
                sources = payload.get("source_docs", [])
            except Exception:
                content, sources = row.assistant_response, []
            
            messages.append({
                "role": "assistant",
                "content": content,
                "sources": sources,
                "timestamp": row.timestamp.isoformat(),
            })
        
        print(f"✅ chat/history API: Retrieved {len(messages)} messages for USER : {user['email']}")
        return JSONResponse(status_code=status.HTTP_200_OK, content={"messages": messages})
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ chat/history error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_history(
    user = Depends(require_role(["Learner", "Instructor", "Admin"])),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete ALL chat messages for the authenticated user.
    Returns 204 No Content on success.
    """
    try:
        user_profile = await get_user_profile_by_email(user["email"], db)
        
        if not user_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="❌ User not found")
        
        await clear_chat_history(user_profile.user_id, db)

        return
    except Exception as e:
        print(f"❌ /chat/history DELETE error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
