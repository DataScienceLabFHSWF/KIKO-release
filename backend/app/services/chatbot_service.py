# # ChatbotService service
import time, logging, json
from datetime import datetime, timezone
from typing import Any, Dict, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from app.core import PromptManager, QAChainManager
from .vector_store_service import similarity_search
from .configuration_service import get_app_config_and_libary_available
from .embedding_service import generate_query_embedding
from app.models import ChatHistoryModel

logger = logging.getLogger(__name__)

async def save_chat_turn(
    user_id: int,
    role: str,
    user_query: str,
    assistant_payload: Dict[str, Any],
    db: AsyncSession
) -> ChatHistoryModel:
    """Save a chat turn (user query and assistant response) to the database.
    This function creates a new ChatHistoryModel record with the provided user ID,
    user query, assistant response, and role, then commits it to the database.
    It returns the created ChatHistoryModel object."""
    try:
        print(f"ℹ️ Saving chat turn for user_id {user_id} with role {role}.")

        row = ChatHistoryModel(
            user_id=user_id,
            role=role,
            user_query=user_query,
            assistant_response=json.dumps(assistant_payload, ensure_ascii=False),
            timestamp=datetime.now(timezone.utc),
        )
        
        db.add(row)

        await db.commit()

        await db.refresh(row)

        print(f"✅ Saved chat turn with chat_id {row.chat_id} for user_id {user_id}.")

        return row
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

async def fetch_chat_history(
    user_id: int,
    db: AsyncSession
) -> List[ChatHistoryModel]:
    """Retrieve chat history for a specific user from the database.
    This function queries the ChatHistoryModel table for records matching the given user ID,
    orders them by timestamp in ascending order.
    It returns a list of ChatHistoryModel objects."""
    try:
        print(f"ℹ️ Fetching chat history for user_id {user_id}.")

        q = (
            select(ChatHistoryModel)
            .where(ChatHistoryModel.user_id == user_id)
            .order_by(ChatHistoryModel.timestamp.asc())
        )
        
        result = await db.execute(q)
        
        if not result:
            return None
        
        response = list(result.scalars().all())
        print(f"✅ Retrieved {len(response)} chat history records for user_id {user_id}.")
        return response
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

async def run_query(
    query: str, 
    embedding_model: str, 
    llm_model: str,
    response_language: str,
    user_id: int,
    user_role: str,
    db: AsyncSession    
    ) -> str:
    """Run a query against the chatbot service.
    This function takes a query string, embedding model, and LLM model,
    retrieves relevant embeddings from the database, and generates an answer using the LLM.
    If no relevant embeddings are found or if the LLM fails to generate an answer, it returns None.
    If the query is successful, it returns the generated answer."""
    
    print(f"ℹ️ Running chatbot query for user:{query}, model: {llm_model}, embedding model: {embedding_model}")

    # Step 1: Generate query embedding
    query_embedding = await generate_query_embedding(query, model_name=embedding_model)
    
    if not query_embedding or len(query_embedding) == 0:
        print("❌ Failed to generate embedding for the query.")
        # "No embeddings generated"
        return None

    print(f"✅ Generated query embedding: {query_embedding} and {len(query_embedding)} dimensions.")   
    
    # Step 2: Fetch similar embeddings
    similar_docs = await similarity_search(
        query_vec=query_embedding,
        embedding_model=embedding_model,
        user_id=user_id,
        user_role=user_role,
        db=db,        
    )

    if not similar_docs:
        print("❌ No relevant embeddings found for the query.")
        # need to send the respose as docs not exists or processed.
        # "No similar embeddings"
        return None
    
    chunks = [e.chunks for e in similar_docs]
    configs = await get_app_config_and_libary_available()
    
    if not configs:
        print("❌ Failed to retrieve application configuration from API.")
        return None
    
    # Step 3: Initialize PromptManager and QAChainManager
    prompt_mgr = PromptManager(configs)
    qa_chain_manager = QAChainManager(prompt_mgr, response_language=response_language)
    
    # Step 4: Run LLM
    answer = await qa_chain_manager.run_qa(
        user_question=query,
        context_docs=chunks,
        llm_model=llm_model
    )

    if not answer:
        print("❌ No answer generated by the LLM.")
        # "no answers"
        return None
    
    source_docs = []    
    for doc in similar_docs:
        if hasattr(doc, 'metadatas'):
            print(f"ℹ️ Processing document metadata: {doc.metadatas}")
            metadata = doc.metadatas.copy()
            # Add search relevance info
            metadata["search_query"] = query
            metadata["retrieved_chunks"] = doc.chunks
            metadata["search_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
            source_docs.append(metadata)
    
    print(f"ℹ️ Found {len(source_docs)} source documents for the answer.")

    response = {
        "answer": answer,
        "source_docs": source_docs
    }

    print(f"✅ Generated Response: {response}")
    # Return the response
    return response

async def clear_chat_history(
    user_id: int, 
    db: AsyncSession
) -> None:
    """
    Delete all chat messages for a given user_id.
    """
    try:
        await db.execute(
            delete(ChatHistoryModel)
            .where(
                ChatHistoryModel.user_id == user_id
            )
        )
        
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while deleting the chat: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error while deleting the chat: {str(e)}"
        )
