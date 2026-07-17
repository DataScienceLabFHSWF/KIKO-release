from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class ChatHistoryModel(Base):
    """model for storing chat history in the database.
    This model includes fields for chat ID, user ID, role, user query, assistant response, and timestamp.
    It is used to manage chat history records within the application."""
    
    __tablename__ = "chat_history"
    chat_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    role = Column(String, nullable=False)
    user_query = Column(Text, nullable=False) # store the user query text
    assistant_response = Column(Text, nullable=False) # store JSON string (answer + sources)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("UserModel", back_populates="chat_histories")
