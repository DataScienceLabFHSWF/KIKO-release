from pydantic import BaseModel

class ChatQueryRequest(BaseModel):
    """Request Schema for chatbot queries. This Schema represents the input for a chatbot query.
    It includes the query string, the embedding model to use, and the LLM model for generating responses."""
    
    query: str
    embedding_model: str
    llm_model: str
