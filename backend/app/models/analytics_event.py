from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, Index
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base

class EventType(str, enum.Enum):
    DOCUMENT_UPLOAD = "document_upload"
    DOCUMENT_PARSED = "document_parsed"
    DOCUMENT_EXTRACTED = "document_extracted"
    DOCUMENT_APPROVED = "document_approved"
    DOCUMENT_REJECTED = "document_rejected"
    DOCUMENT_ESCALATED = "document_escalated"
    DOCUMENT_DELETED = "document_deleted"
    DOCUMENT_EXPORTED = "document_exported"
    CHAT_INTERACTION = "chat_interaction"
    EXTRACTION_RETRY = "extraction_retry"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    document_id = Column(Integer, nullable=True, index=True)
    user_id = Column(String(100), nullable=True, index=True)
    session_id = Column(String(100), nullable=True)
    
    # Event metadata stored as JSON for flexibility
    event_data = Column(JSON, nullable=True)
    
    # Performance metrics
    duration_ms = Column(Float, nullable=True)  # For tracking operation duration
    
    # Client information
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    client_version = Column(String(20), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Indexes for common queries
    __table_args__ = (
        # Composite index for time-based queries by event type
        Index('idx_event_type_created', 'event_type', 'created_at'),
        # Index for user activity queries
        Index('idx_user_created', 'user_id', 'created_at'),
        # Index for document activity queries
        Index('idx_document_created', 'document_id', 'created_at'),
    )