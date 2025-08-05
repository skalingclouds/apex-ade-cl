from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
import aiofiles
import os
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.models.document import Document, DocumentStatus
from app.schemas.document import DocumentResponse, DocumentListResponse, DocumentUpdate

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a PDF document for processing"""
    
    # Validate file size
    if file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE} bytes"
        )
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    filepath = os.path.join(settings.UPLOAD_DIRECTORY, filename)
    
    # Save file
    async with aiofiles.open(filepath, 'wb') as f:
        content = await file.read()
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
    
    # Delete file from filesystem
    if os.path.exists(document.filepath):
        os.remove(document.filepath)
    
    # Delete from database
    db.delete(document)
    db.commit()

@router.post("/{document_id}/approve", response_model=DocumentResponse)
def approve_document(
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
    
    document.status = DocumentStatus.APPROVED
    db.commit()
    db.refresh(document)
    return document

@router.post("/{document_id}/reject", response_model=DocumentResponse)
def reject_document(
    document_id: int,
    reason: str = None,
    db: Session = Depends(get_db)
):
    """Reject a document's extraction results"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    document.status = DocumentStatus.REJECTED
    if reason:
        document.error_message = reason
    db.commit()
    db.refresh(document)
    return document

@router.post("/{document_id}/escalate", response_model=DocumentResponse)
def escalate_document(
    document_id: int,
    reason: str = None,
    db: Session = Depends(get_db)
):
    """Escalate a document for further review"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    document.status = DocumentStatus.ESCALATED
    if reason:
        document.error_message = reason
    db.commit()
    db.refresh(document)
    return document