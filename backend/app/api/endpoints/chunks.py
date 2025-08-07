"""
API endpoints for document chunk management and progress tracking
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
import logging

from app.core.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import (
    DocumentChunk, ChunkStatus, ProcessingLog, 
    ProcessingMetrics, ExtractionMethod
)
from app.services.pdf_chunker import PDFChunker
from app.services.chunk_processor import ChunkProcessor
from app.schemas.extraction import ExtractionRequest

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/{document_id}/chunk")
async def create_document_chunks(
    document_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create chunks for a large document
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if already chunked
    if document.is_chunked:
        return {
            "message": "Document already chunked",
            "total_chunks": document.total_chunks
        }
    
    # Initialize chunker
    chunker = PDFChunker()
    
    # Check if document needs chunking
    should_chunk, page_count, file_size_mb = await chunker.should_chunk_document(document.filepath)
    
    if not should_chunk:
        return {
            "message": "Document doesn't require chunking",
            "page_count": page_count,
            "file_size_mb": file_size_mb
        }
    
    # Create chunks
    chunks = await chunker.create_chunks(document, db)
    
    return {
        "message": "Chunks created successfully",
        "total_chunks": len(chunks),
        "page_count": page_count,
        "file_size_mb": file_size_mb,
        "chunks": [
            {
                "chunk_number": c.chunk_number,
                "pages": f"{c.start_page}-{c.end_page}",
                "status": c.status
            } for c in chunks
        ]
    }

@router.post("/{document_id}/process-chunks")
async def process_document_chunks(
    document_id: int,
    extraction_request: ExtractionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Process all chunks for a document with selected fields
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if document is chunked
    if not document.is_chunked:
        # Create chunks first if needed
        chunker = PDFChunker()
        should_chunk, _, _ = await chunker.should_chunk_document(document.filepath)
        
        if should_chunk:
            await chunker.create_chunks(document, db)
        else:
            # Process as single document
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document doesn't require chunk processing. Use regular extraction."
            )
    
    # Start processing in background
    processor = ChunkProcessor(db)
    
    # Start async processing
    background_tasks.add_task(
        processor.process_document_chunks,
        document,
        extraction_request.selected_fields,
        extraction_request.custom_fields
    )
    
    return {
        "message": "Chunk processing started",
        "document_id": document_id,
        "total_chunks": document.total_chunks,
        "status": "PROCESSING"
    }

@router.get("/{document_id}/chunks")
def get_document_chunks(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all chunks for a document with their status
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    chunks = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).order_by(DocumentChunk.chunk_number).all()
    
    return {
        "document_id": document_id,
        "total_chunks": len(chunks),
        "chunks": [
            {
                "id": chunk.id,
                "chunk_number": chunk.chunk_number,
                "pages": f"{chunk.start_page}-{chunk.end_page}",
                "page_count": chunk.page_count,
                "status": chunk.status,
                "extraction_method": chunk.extraction_method,
                "processing_time_ms": chunk.processing_time_ms,
                "retry_count": chunk.retry_count,
                "error_message": chunk.error_message
            } for chunk in chunks
        ]
    }

@router.get("/{document_id}/chunk/{chunk_id}")
def get_chunk_details(
    document_id: int,
    chunk_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific chunk
    """
    chunk = db.query(DocumentChunk).filter(
        DocumentChunk.id == chunk_id,
        DocumentChunk.document_id == document_id
    ).first()
    
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chunk not found"
        )
    
    # Get recent logs for this chunk
    logs = db.query(ProcessingLog).filter(
        ProcessingLog.chunk_id == chunk_id
    ).order_by(desc(ProcessingLog.created_at)).limit(10).all()
    
    return {
        "chunk": {
            "id": chunk.id,
            "chunk_number": chunk.chunk_number,
            "pages": f"{chunk.start_page}-{chunk.end_page}",
            "page_count": chunk.page_count,
            "status": chunk.status,
            "file_path": chunk.file_path,
            "file_size_mb": chunk.file_size_mb,
            "extraction_method": chunk.extraction_method,
            "extracted_fields": chunk.extracted_fields,
            "processing_time_ms": chunk.processing_time_ms,
            "retry_count": chunk.retry_count,
            "error_message": chunk.error_message,
            "created_at": chunk.created_at,
            "processing_started_at": chunk.processing_started_at,
            "processing_completed_at": chunk.processing_completed_at
        },
        "logs": [
            {
                "action": log.action,
                "level": log.level,
                "message": log.message,
                "extraction_method": log.extraction_method,
                "created_at": log.created_at
            } for log in logs
        ]
    }

@router.post("/{document_id}/chunk/{chunk_id}/retry")
async def retry_chunk_processing(
    document_id: int,
    chunk_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Retry processing a failed chunk
    """
    chunk = db.query(DocumentChunk).filter(
        DocumentChunk.id == chunk_id,
        DocumentChunk.document_id == document_id
    ).first()
    
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chunk not found"
        )
    
    if chunk.status not in [ChunkStatus.FAILED, ChunkStatus.RETRYING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Chunk is not in a retryable state. Current status: {chunk.status}"
        )
    
    # Reset chunk for retry
    chunk.status = ChunkStatus.PENDING
    chunk.error_message = None
    db.commit()
    
    # Get document and extraction settings
    document = db.query(Document).filter(Document.id == document_id).first()
    
    # TODO: Get original extraction settings from somewhere
    # For now, we'll need to pass them in the request
    
    return {
        "message": "Chunk retry initiated",
        "chunk_id": chunk_id,
        "status": "PENDING"
    }

@router.get("/{document_id}/progress")
def get_processing_progress(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get real-time processing progress for a document
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Get processing metrics
    metrics = db.query(ProcessingMetrics).filter(
        ProcessingMetrics.document_id == document_id
    ).first()
    
    if not metrics:
        return {
            "document_id": document_id,
            "status": document.status,
            "is_chunked": document.is_chunked,
            "progress": 0,
            "message": "No processing metrics available"
        }
    
    # Calculate progress percentage
    progress_percentage = 0
    if metrics.total_chunks > 0:
        progress_percentage = (metrics.completed_chunks / metrics.total_chunks) * 100
    
    # Get current processing chunk
    current_chunk = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id,
        DocumentChunk.status == ChunkStatus.PROCESSING
    ).first()
    
    # Estimate time remaining
    time_remaining_seconds = None
    if metrics.avg_chunk_time_ms and metrics.total_chunks > metrics.completed_chunks:
        remaining_chunks = metrics.total_chunks - metrics.completed_chunks
        time_remaining_seconds = (remaining_chunks * metrics.avg_chunk_time_ms) / 1000
    
    return {
        "document_id": document_id,
        "status": document.status,
        "progress": {
            "percentage": round(progress_percentage, 2),
            "completed_chunks": metrics.completed_chunks,
            "total_chunks": metrics.total_chunks,
            "failed_chunks": metrics.failed_chunks,
            "processed_pages": metrics.processed_pages,
            "total_pages": metrics.total_pages
        },
        "current_chunk": {
            "chunk_number": current_chunk.chunk_number,
            "pages": f"{current_chunk.start_page}-{current_chunk.end_page}"
        } if current_chunk else None,
        "performance": {
            "avg_chunk_time_ms": metrics.avg_chunk_time_ms,
            "total_processing_time_ms": metrics.total_processing_time_ms,
            "time_remaining_seconds": time_remaining_seconds
        },
        "extraction_methods": {
            "landing_ai_api": metrics.landing_ai_api_count,
            "landing_ai_sdk": metrics.landing_ai_sdk_count,
            "openai_fallback": metrics.openai_fallback_count
        },
        "is_complete": metrics.is_complete,
        "has_failures": metrics.has_failures
    }

@router.get("/{document_id}/logs")
def get_processing_logs(
    document_id: int,
    limit: int = 50,
    level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get processing logs for a document
    """
    query = db.query(ProcessingLog).filter(
        ProcessingLog.document_id == document_id
    )
    
    if level:
        query = query.filter(ProcessingLog.level == level)
    
    logs = query.order_by(desc(ProcessingLog.created_at)).limit(limit).all()
    
    return {
        "document_id": document_id,
        "total_logs": len(logs),
        "logs": [
            {
                "id": log.id,
                "chunk_id": log.chunk_id,
                "action": log.action,
                "level": log.level,
                "message": log.message,
                "extraction_method": log.extraction_method,
                "metadata": log.log_metadata,
                "created_at": log.created_at
            } for log in logs
        ]
    }

@router.delete("/{document_id}/chunks")
async def cleanup_document_chunks(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Clean up chunk files after processing is complete
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Only allow cleanup if processing is complete
    if document.status not in [DocumentStatus.EXTRACTED, DocumentStatus.APPROVED, DocumentStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cleanup chunks while document is in {document.status} status"
        )
    
    # Clean up chunk files
    chunker = PDFChunker()
    await chunker.cleanup_chunks(document_id)
    
    # Optionally, delete chunk records from database
    # db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
    # db.commit()
    
    return {
        "message": "Chunk files cleaned up successfully",
        "document_id": document_id
    }