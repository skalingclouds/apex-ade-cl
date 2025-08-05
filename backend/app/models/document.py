from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base

class DocumentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PARSING = "PARSING"
    PARSED = "PARSED"
    EXTRACTING = "EXTRACTING"
    EXTRACTED = "EXTRACTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"
    FAILED = "FAILED"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    extracted_md = Column(Text, nullable=True)
    extracted_data = Column(Text, nullable=True)  # JSON string of extracted data
    error_message = Column(Text, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    extraction_schemas = relationship("ExtractionSchema", back_populates="document", cascade="all, delete-orphan")
    chat_logs = relationship("ChatLog", back_populates="document", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="document", cascade="all, delete-orphan")