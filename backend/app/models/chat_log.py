from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    highlighted_areas = Column(Text, nullable=True)  # JSON string of highlight coordinates
    fallback = Column(Boolean, default=False, nullable=False)
    
    # Additional fields for OpenAI integration
    user_id = Column(String(255), nullable=True, index=True)
    model_used = Column(String(100), nullable=True)  # Track which AI model was used
    confidence = Column(String(10), nullable=True)  # Store confidence score
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="chat_logs")