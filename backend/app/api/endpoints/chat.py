from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from starlette.requests import Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import json
import time
import logging

from app.core.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.chat_log import ChatLog
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.audit_service import AuditService
from app.services.analytics_service import AnalyticsService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/{document_id}/chat", response_model=ChatResponse)
async def chat_with_document(
    request: Request,
    background_tasks: BackgroundTasks,
    document_id: int,
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Send a chat query about the document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.status not in [DocumentStatus.EXTRACTED, DocumentStatus.APPROVED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document must be extracted before chat is available"
        )
    
    try:
        # Track processing time
        start_time = time.time()
        
        # Process chat query
        chat_service = ChatService()
        response_data = await chat_service.process_query(
            document_path=document.filepath,
            document_text=document.extracted_md,
            query=chat_request.query
        )
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Save chat log with retry logic
        chat_log = ChatLog(
            document_id=document_id,
            query=chat_request.query,
            response=response_data.response,
            highlighted_areas=json.dumps([area.dict() for area in response_data.highlighted_areas])
            if response_data.highlighted_areas else None,
            fallback=response_data.fallback
        )
        
        # Retry logic for database operations
        max_retries = 2
        retry_count = 0
        last_error = None
        
        while retry_count < max_retries:
            try:
                db.add(chat_log)
                db.commit()
                db.refresh(chat_log)
                break  # Success, exit retry loop
            except SQLAlchemyError as e:
                retry_count += 1
                last_error = e
                logger.warning(f"Failed to save chat log (attempt {retry_count}/{max_retries}): {str(e)}")
                db.rollback()
                
                if retry_count < max_retries:
                    time.sleep(0.5)  # Wait before retry
                else:
                    # All retries failed, create response without saved log
                    logger.error(f"Failed to save chat log after {max_retries} attempts: {str(e)}")
                    # Still return the response but indicate storage failure
                    raise HTTPException(
                        status_code=status.HTTP_207_MULTI_STATUS,
                        detail={
                            "message": "Chat response generated but failed to save to history",
                            "response": response_data.response,
                            "highlighted_areas": [area.dict() for area in response_data.highlighted_areas] if response_data.highlighted_areas else [],
                            "fallback": response_data.fallback,
                            "storage_error": True,
                            "retry_available": True
                        }
                    )
        
        # Audit log document access via chat
        audit_service = AuditService(db, request)
        audit_service.log_document_access(
            document_id=document_id,
            action="chat"
        )
        
        # Analytics event logging
        analytics_service = AnalyticsService(db, request, background_tasks)
        analytics_service.log_chat_interaction(
            document_id=document_id,
            query=chat_request.query,
            response_length=len(response_data.response),
            highlighted_areas=len(response_data.highlighted_areas) if response_data.highlighted_areas else 0,
            fallback=response_data.fallback,
            duration_ms=duration_ms
        )
        
        return ChatResponse(
            id=chat_log.id,
            query=chat_log.query,
            response=chat_log.response,
            highlighted_areas=response_data.highlighted_areas,
            fallback=response_data.fallback,
            created_at=chat_log.created_at
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions (like our storage failure)
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat query: {str(e)}"
        )

@router.get("/{document_id}/chat/history", response_model=List[ChatResponse])
def get_chat_history(
    document_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get chat history for a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    chat_logs = db.query(ChatLog).filter(
        ChatLog.document_id == document_id
    ).order_by(ChatLog.created_at.desc()).offset(skip).limit(limit).all()
    
    responses = []
    for log in chat_logs:
        highlighted_areas = None
        if log.highlighted_areas:
            highlighted_areas = json.loads(log.highlighted_areas)
        
        responses.append(ChatResponse(
            id=log.id,
            query=log.query,
            response=log.response,
            highlighted_areas=highlighted_areas,
            fallback=getattr(log, 'fallback', False),  # Get fallback from log or default to False
            created_at=log.created_at
        ))
    
    return responses