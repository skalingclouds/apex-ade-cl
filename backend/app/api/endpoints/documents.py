from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, BackgroundTasks
from starlette.requests import Request
from sqlalchemy.orm import Session
import aiofiles
import os
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.models.document import Document, DocumentStatus
from app.schemas.document import DocumentResponse, DocumentListResponse, DocumentUpdate, RejectRequest, EscalateRequest
from app.services.audit_service import AuditService
from app.services.analytics_service import AnalyticsService

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a PDF document for processing"""
    
    print(f"Upload request received - filename: {file.filename if file else 'No file'}")
    
    # Read file content first to check size
    content = await file.read()
    file_size = len(content)
    
    # Validate file size
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024*1024*1024):.1f}GB"
        )
    
    # Validate file type
    print(f"File validation - filename: {file.filename}, ends with pdf: {file.filename.lower().endswith('.pdf')}")
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    filepath = os.path.join(settings.UPLOAD_DIRECTORY, filename)
    
    # Save file (content already read above)
    async with aiofiles.open(filepath, 'wb') as f:
        await f.write(content)
    
    # Create database entry
    db_document = Document(
        filename=file.filename,
        filepath=filepath,
        status=DocumentStatus.PENDING
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Audit log the upload
    audit_service = AuditService(db, request)
    audit_service.log_document_access(
        document_id=db_document.id,
        action="upload"
    )
    
    # Analytics event logging (non-blocking)
    analytics_service = AnalyticsService(db, request, background_tasks)
    analytics_service.log_document_upload(
        document_id=db_document.id,
        filename=file.filename,
        file_size=file.size
    )
    
    return db_document

@router.get("/", response_model=DocumentListResponse)
def get_documents(
    skip: int = 0,
    limit: int = 100,
    status: DocumentStatus = None,
    db: Session = Depends(get_db)
):
    """Get list of documents with optional filtering"""
    query = db.query(Document)
    
    if status:
        query = query.filter(Document.status == status)
    
    total = query.count()
    documents = query.offset(skip).limit(limit).all()
    
    return DocumentListResponse(documents=documents, total=total)

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific document by ID"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document

@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db)
):
    """Update document status or metadata"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    for field, value in document_update.dict(exclude_unset=True).items():
        setattr(document, field, value)
    
    db.commit()
    db.refresh(document)
    return document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    request: Request,
    document_id: int,
    db: Session = Depends(get_db)
):
    """Delete a document and its associated data"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Prepare document data for audit logging before deletion
    document_data = {
        "filename": document.filename,
        "uploaded_at": document.uploaded_at.isoformat() if document.uploaded_at else None,
        "status": document.status.value if document.status else None
    }
    
    # Audit log the deletion for GDPR compliance
    audit_service = AuditService(db, request)
    audit_service.log_deletion(
        document_id=document_id,
        document_data=document_data
    )
    
    # Delete file from filesystem
    if os.path.exists(document.filepath):
        os.remove(document.filepath)
    
    # Delete from database
    db.delete(document)
    db.commit()

@router.post("/{document_id}/approve", response_model=DocumentResponse)
def approve_document(
    request: Request,
    background_tasks: BackgroundTasks,
    document_id: int,
    db: Session = Depends(get_db)
):
    """Approve a document's extraction results"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.status != DocumentStatus.EXTRACTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document must be in 'extracted' status to approve"
        )
    
    old_status = document.status
    document.status = DocumentStatus.APPROVED
    db.commit()
    
    # Audit log
    audit_service = AuditService(db, request)
    audit_service.log_status_change(
        document_id=document_id,
        old_status=old_status,
        new_status=DocumentStatus.APPROVED
    )
    
    # Analytics event logging
    analytics_service = AnalyticsService(db, request, background_tasks)
    analytics_service.log_document_status_change(
        document_id=document_id,
        old_status=old_status.value,
        new_status=DocumentStatus.APPROVED.value
    )
    
    db.refresh(document)
    return document

@router.post("/{document_id}/reject", response_model=DocumentResponse)
def reject_document(
    request: Request,
    background_tasks: BackgroundTasks,
    document_id: int,
    reject_request: RejectRequest,
    db: Session = Depends(get_db)
):
    """Reject a document's extraction results"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    old_status = document.status
    document.status = DocumentStatus.REJECTED
    if reject_request.reason:
        document.error_message = reject_request.reason
    db.commit()
    
    # Audit log
    audit_service = AuditService(db, request)
    audit_service.log_status_change(
        document_id=document_id,
        old_status=old_status,
        new_status=DocumentStatus.REJECTED,
        reason=reject_request.reason
    )
    
    # Analytics event logging
    analytics_service = AnalyticsService(db, request, background_tasks)
    analytics_service.log_document_status_change(
        document_id=document_id,
        old_status=old_status.value,
        new_status=DocumentStatus.REJECTED.value,
        reason=reject_request.reason
    )
    
    db.refresh(document)
    return document

@router.post("/{document_id}/escalate", response_model=DocumentResponse)
def escalate_document(
    request: Request,
    background_tasks: BackgroundTasks,
    document_id: int,
    escalate_request: EscalateRequest,
    db: Session = Depends(get_db)
):
    """Escalate a document for further review"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    old_status = document.status
    document.status = DocumentStatus.ESCALATED
    if escalate_request.reason:
        document.error_message = escalate_request.reason
    db.commit()
    
    # Audit log
    audit_service = AuditService(db, request)
    audit_service.log_status_change(
        document_id=document_id,
        old_status=old_status,
        new_status=DocumentStatus.ESCALATED,
        reason=escalate_request.reason
    )
    
    # Analytics event logging
    analytics_service = AnalyticsService(db, request, background_tasks)
    analytics_service.log_document_status_change(
        document_id=document_id,
        old_status=old_status.value,
        new_status=DocumentStatus.ESCALATED.value,
        reason=escalate_request.reason
    )
    
    db.refresh(document)
    return document