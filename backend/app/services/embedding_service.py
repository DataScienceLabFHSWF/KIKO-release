# backend/app/services/embedding_service.py
import os, logging, asyncio
from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import insert as pginsert
from langchain_ollama import OllamaEmbeddings
from app.models import EmbeddingModel, DocumentModel

logger = logging.getLogger(__name__)
EMBEDDING_VECTOR_DB_DIM = int(os.getenv("EMBEDDING_VECTOR_DB_DIM"))
DOCKER_OLLAMA_URL = os.getenv("DOCKER_OLLAMA_URL")

@lru_cache(maxsize=8)
def get_embedding_model(model_name: str) -> OllamaEmbeddings:
    """Get or initialize an Ollama Embeddings instance."""
    try:
        if not model_name:
            raise ValueError("❌ Embedding model name is required.")
        
        if not DOCKER_OLLAMA_URL:
            raise ValueError("❌ DOCKER_OLLAMA_URL is not configured.")
        
        print(f"ℹ️ Getting Embeddings instance for model: {model_name} and {DOCKER_OLLAMA_URL}")
        
        emb = OllamaEmbeddings(
            model=model_name,
            base_url=DOCKER_OLLAMA_URL
        )
        print(f"✅ Initialized new Embeddings instance for model: {emb}")
        return emb
    except Exception as e:
        print(f"❌ Failed to init Ollama Embeddings '{model_name}': {e}")
        return None

def _validate_embedding_vector(
    vector: list[float], 
    label: str
) -> None:
    if not isinstance(vector, list) or not vector:
        raise ValueError(f"❌ {label} embedding is empty.")

    if len(vector) != EMBEDDING_VECTOR_DB_DIM:
        raise ValueError(
            f"❌ {label} embedding dimension mismatch: "
            f"got {len(vector)}, expected {EMBEDDING_VECTOR_DB_DIM}"
        )

async def generate_query_embedding(
    query: str,
    model_name: str,
) -> list[float] | None:
    try:
        if not query or not query.strip():
            raise ValueError("❌ Empty query cannot be embedded.")
        
        model = get_embedding_model(model_name)
        
        vector = await asyncio.to_thread(model.embed_query, query.strip())

        _validate_embedding_vector(vector, "Query")

        return vector
    except Exception as e:
        logger.exception("❌ Failed to generate query embedding")
        return None

async def generate_document_embeddings(
    texts: list[str],
    model_name: str,
) -> list[list[float]] | None:
    try:
        clean_texts = [
            text.strip()
            for text in texts
            if isinstance(text, str) and text.strip()
        ]

        if not clean_texts:
            raise ValueError("❌ No texts provided for embedding.")

        model = get_embedding_model(model_name)
        
        vectors = await asyncio.to_thread(model.embed_documents, clean_texts)

        if not vectors or len(vectors) != len(clean_texts):
            raise ValueError(
                f"❌ Embedding count mismatch: got {len(vectors or [])}, expected {len(clean_texts)}"
            )

        for vector in vectors:
            _validate_embedding_vector(vector, "Document")

        return vectors
    except Exception as e:
        logger.exception("❌ Failed to generate document embeddings")
        return None
  
async def store_embeddings_to_db(
    chunks: list[str], 
    metadatas: list[dict], 
    embeddings: list[list[float]], 
    embedding_model_name: str, 
    doc_id: int, 
    user_id: int, 
    db: AsyncSession
):
    """Store embeddings in the database.
    This function takes a list of text chunks, their corresponding metadata, and embeddings, and stores them in the database.
    It pads the embeddings to match the fixed dimension defined by EMBEDDING_VECTOR_DB_DIM.
    If the database operation fails, it raises an HTTPException."""

    try:
        if not (len(chunks) == len(metadatas) == len(embeddings)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"❌ Alignment error: "
                    f"{len(chunks)} chunks, {len(metadatas)} metadatas, {len(embeddings)} embeddings"
                )
            )
        
        print(f"ℹ️ Storing the embeddings. {len(embeddings)} embeddings to the database.")
        
        records = []
            
        for i, (chunk, meta, emb) in enumerate(zip(chunks, metadatas, embeddings)):
            record = dict(
                chunks= chunk,
                metadatas= meta,
                embedding= emb,
                embedding_model= embedding_model_name,
                document_id= doc_id,
                chunk_id= i,
                doc_uploaded_by=user_id
            )

            records.append(record)
            
        stmt = pginsert(EmbeddingModel).values(records)
        
        stmt = stmt.on_conflict_do_nothing(
            index_elements=["document_id", "embedding_model", "chunk_id"]
        )
        
        await db.execute(stmt)
        await db.commit()
        print(f"✅ Successfully stored the Embeddings to DB.")
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error during add_embeddings in DB: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during add_embeddings in DB: {str(e)}"
        )
    
async def get_embeddings_from_db(
    content_hash: str, 
    embedding_model: str, 
    user_id: int, 
    db: AsyncSession
) -> list[EmbeddingModel]:
    """Retrieve embeddings from the database by file hash and embedding model.
    This function fetches embeddings from the database based on the provided file hash name, embedding model, and user ID.
    It returns a list of EmbeddingModel objects if found, or None if not found.
    If the database operation fails, it raises an HTTPException."""
        
    try:
        print(f"ℹ️ Getting the Embedding by file hash: {content_hash} and {embedding_model}.")

        result = await db.execute(
            select(EmbeddingModel)
            .join(DocumentModel, EmbeddingModel.document_id == DocumentModel.document_id)
            .where(
                and_(
                    DocumentModel.content_hash == content_hash,
                    DocumentModel.status == "processed",
                    EmbeddingModel.embedding_model == embedding_model,
                    EmbeddingModel.doc_uploaded_by == user_id
                )
            )
            .options(selectinload(EmbeddingModel.document))
        )

        embeddings = result.scalars().all()
            
        if embeddings is None:
            return None
            
        print(f"✅ Successfully got the Embeddings from DB.")
        return embeddings
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Database error during get_embeddings from DB: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"❌ Unexpected error during get_embeddings from DB: {str(e)}"
        )
