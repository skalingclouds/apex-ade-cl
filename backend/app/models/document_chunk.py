"""
Document chunk model for processing large PDFs in segments
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from enum import Enum

class ChunkStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"

class ExtractionMethod(str, Enum):
    LANDING_AI_API = "LANDING_AI_API"
    LANDING_AI_SDK = "LANDING_AI_SDK"
    OPENAI_FALLBACK = "OPENAI_FALLBACK"
    MANUAL = "MANUAL"

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    chunk_number = Column(Integer, nullable=False)
    start_page = Column(Integer, nullable=False)
    end_page = Column(Integer, nullable=False)
    page_count = Column(Integer, nullable=False)
    status = Column(String, default=ChunkStatus.PENDING, nullable=False, index=True)
    file_path = Column(Text)  # Path to the chunk PDF file
    
    # Extraction tracking
    extraction_method = Column(String)  # Which method successfully extracted
    extracted_data = Column(JSON)
    extracted_fields = Column(JSON)  # Which fields were extracted from this chunk
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Performance metrics
    file_size_mb = Column(Float)
    processing_time_ms = Column(Integer)
    api_calls_made = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    last_retry_at = Column(DateTime)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    processing_logs = relationship("ProcessingLog", back_populates="chunk", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, chunk={self.chunk_number}, status={self.status})>"

class ProcessingLog(Base):
    __tablename__ = "processing_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    chunk_id = Column(Integer, ForeignKey("document_chunks.id"), index=True)
    
    # Log details
    action = Column(String, nullable=False)  # CHUNK_CREATED, EXTRACTION_START, API_CALL, RETRY, SUCCESS, FAILURE
    level = Column(String, default="INFO")  # INFO, WARNING, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    extraction_method = Column(String)  # Track which method was used
    
    # Additional context
    log_metadata = Column(JSON)  # Store any additional data (API response times, error codes, etc.)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    document = relationship("Document", back_populates="processing_logs")
    chunk = relationship("DocumentChunk", back_populates="processing_logs")
    
    def __repr__(self):
        return f"<ProcessingLog(id={self.id}, action={self.action}, chunk_id={self.chunk_id})>"

class ProcessingMetrics(Base):
    __tablename__ = "processing_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), unique=True, nullable=False)
    
    # Overall metrics
    total_pages = Column(Integer, nullable=False)
    total_chunks = Column(Integer, nullable=False)
    processed_pages = Column(Integer, default=0)
    completed_chunks = Column(Integer, default=0)
    failed_chunks = Column(Integer, default=0)
    
    # Extraction method usage counts
    landing_ai_api_count = Column(Integer, default=0)
    landing_ai_sdk_count = Column(Integer, default=0)
    openai_fallback_count = Column(Integer, default=0)
    
    # Performance metrics
    avg_chunk_time_ms = Column(Float)
    total_processing_time_ms = Column(Integer, default=0)
    total_api_calls = Column(Integer, default=0)
    
    # Cost tracking (if needed)
    estimated_cost = Column(Float, default=0.0)
    
    # Status
    is_complete = Column(Boolean, default=False)
    has_failures = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    estimated_completion = Column(DateTime)
    actual_completion = Column(DateTime)
    
    # Relationships
    document = relationship("Document", back_populates="processing_metrics", uselist=False)
    
    def __repr__(self):
        return f"<ProcessingMetrics(document_id={self.document_id}, progress={self.completed_chunks}/{self.total_chunks})>"