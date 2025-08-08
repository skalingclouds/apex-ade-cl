from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Boolean, Float
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
    CHUNKING = "CHUNKING"  # New status for chunking process
    CHUNK_PROCESSING = "CHUNK_PROCESSING"  # Processing chunks

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    extracted_md = Column(Text, nullable=True)
    extracted_data = Column(Text, nullable=True)  # JSON string of extracted data
    parsed_fields = Column(Text, nullable=True)  # JSON string of parsed field definitions
    error_message = Column(Text, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Archive fields for soft delete
    archived = Column(Boolean, default=False, nullable=False)
    archived_at = Column(DateTime(timezone=True), nullable=True)
    archived_by = Column(String(255), nullable=True)
    
    # Chunking fields for large documents
    is_chunked = Column(Boolean, default=False, nullable=False)
    total_chunks = Column(Integer, default=0)
    completed_chunks = Column(Integer, default=0)
    file_size_mb = Column(Float)
    page_count = Column(Integer)
    chunk_size = Column(Integer, default=40)  # Pages per chunk (optimized for paid plan)
    processing_strategy = Column(String, default="SEQUENTIAL")  # SEQUENTIAL, PARALLEL, ADAPTIVE
    
    # Relationships
    extraction_schemas = relationship("ExtractionSchema", back_populates="document", cascade="all, delete-orphan")
    chat_logs = relationship("ChatLog", back_populates="document", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="document", cascade="all, delete-orphan")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    processing_logs = relationship("ProcessingLog", back_populates="document", cascade="all, delete-orphan")
    processing_metrics = relationship("ProcessingMetrics", back_populates="document", uselist=False, cascade="all, delete-orphan")