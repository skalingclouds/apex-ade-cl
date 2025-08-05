from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from app.core.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.chat_log import ChatLog
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()

@router.post("/{document_id}/chat", response_model=ChatResponse)
async def chat_with_document(
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
        # Process chat query
        chat_service = ChatService()
        response_data = await chat_service.process_query(
            document_path=document.filepath,
            document_text=document.extracted_md,
            query=chat_request.query
        )
        
        # Save chat log
        chat_log = ChatLog(
            document_id=document_id,
            query=chat_request.query,
            response=response_data.response,
            highlighted_areas=json.dumps([area.dict() for area in response_data.highlighted_areas])
            if response_data.highlighted_areas else None
        )
        db.add(chat_log)
        db.commit()
        db.refresh(chat_log)
        
        return ChatResponse(
            id=chat_log.id,
            query=chat_log.query,
            response=chat_log.response,
            highlighted_areas=response_data.highlighted_areas,
            created_at=chat_log.created_at
        )
        
    except Exception as e:
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
            created_at=log.created_at
        ))
    
    return responses