from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from sqlalchemy import select
from app.models import EmbeddingModel, UserModel

async def similarity_search(
    query_vec: list[float],
    embedding_model: str,
    user_id: int,
    user_role: str,
    db: AsyncSession,
    top_k: int = 5
) -> list[EmbeddingModel]:
    """Perform similarity search using cosine similarity directly in the database.
    This function queries the EmbeddingModel table to find the top_k most similar embeddings
    to the provided query vector for a specific user and embedding model.
    If no embeddings are found for the user, it falls back to searching for embeddings
    created by the admin (user_id=3).
    Returns a list of EmbeddingModel objects representing the most similar embeddings.
    """
        
    try:
        print(f"ℹ️ Searching for top-{top_k} similar embeddings for user_id={user_id} , role={user_role} and model={embedding_model}")

        if user_role in ["Instructor", "Admin"]:
            # For Instructors and Admins, search only for their own embeddings generated for documents uploaded by themselves.
            stmt = (
                select(EmbeddingModel)
                .where(
                    EmbeddingModel.embedding_model == embedding_model,
                    EmbeddingModel.doc_uploaded_by == user_id
                )
                .order_by(EmbeddingModel.embedding.cosine_distance(query_vec).asc())
                .limit(top_k)
            )
            
            result = await db.execute(stmt)
            
            embeddings = result.scalars().all()
            
            return embeddings
        else:
            # Learner: first search for embeddings uploaded by the learner
            stmt = (
                select(EmbeddingModel)
                .where(
                    EmbeddingModel.embedding_model == embedding_model,
                    EmbeddingModel.doc_uploaded_by == user_id 
                )
                .order_by(EmbeddingModel.embedding.cosine_distance(query_vec).asc())
                .limit(top_k)
            )
            
            result = await db.execute(stmt)
            
            embeddings = result.scalars().all()
            if embeddings:
                return embeddings
            
            # Fallback: search embeddings uploaded by users with role "Instructor"
            stmt_instructors = (
                select(EmbeddingModel)
                .join(UserModel, UserModel.user_id == EmbeddingModel.doc_uploaded_by)
                .where(
                    EmbeddingModel.embedding_model == embedding_model,
                    UserModel.role == "Instructor"
                )
                .order_by(EmbeddingModel.embedding.cosine_distance(query_vec).asc())
                .limit(top_k)
            )
            
            result = await db.execute(stmt_instructors)
            
            embeddings = result.scalars().all()
            
            return embeddings
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error during Searching the similarity for query using cosine_similarity in DB: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during Searching the similarity for query using cosine_similarity in DB: {str(e)}"
        )
