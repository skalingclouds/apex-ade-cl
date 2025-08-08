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
from app.schemas.extraction import ParseResponse, FieldInfo, ExtractionRequest
from app.services.audit_service import AuditService
from app.services.analytics_service import AnalyticsService

router = APIRouter()

async def process_large_document_async(document_id: int, filepath: str):
    """Background task to ONLY chunk large documents (NOT extract yet)"""
    from app.core.database import SessionLocal
    from app.services.pdf_chunker import PDFChunker
    
    db = SessionLocal()
    try:
        print(f"Starting async chunking for document {document_id}")
        
        # Initialize chunker only
        chunker = PDFChunker()
        
        # Get the document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Create chunks with 45-page limit for future extraction
        chunks = await chunker.create_chunks(document, db, chunk_size=45)
        print(f"Created {len(chunks)} chunks (max 45 pages each) for document {document_id}")
        
        # Update document status to PENDING (ready for parsing/extraction)
        # DO NOT automatically extract - wait for user to select fields
        document.status = DocumentStatus.PENDING
        db.commit()
        print(f"Document {document_id} chunking complete, ready for user field selection")
        
    except Exception as e:
        print(f"Error processing large document {document_id}: {str(e)}")
        # Update document status to failed
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = DocumentStatus.FAILED
            document.error_message = f"Chunking failed: {str(e)}"
            db.commit()
    finally:
        db.close()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a PDF document for processing - supports streaming for large files"""
    
    print(f"Upload request received - filename: {file.filename if file else 'No file'}")
    
    # Validate file type first
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
    
    # Stream file to disk in chunks to handle large files efficiently
    file_size = 0
    chunk_size = 1024 * 1024 * 10  # 10MB chunks for streaming
    
    print(f"Starting streaming upload for {file.filename}")
    
    try:
        async with aiofiles.open(filepath, 'wb') as f:
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                file_size += len(chunk)
                
                # Check size limit during streaming
                if file_size > settings.MAX_UPLOAD_SIZE:
                    # Clean up partial file
                    await f.close()
                    os.remove(filepath)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024*1024*1024):.1f}GB"
                    )
                
                await f.write(chunk)
                print(f"Streamed {file_size / (1024*1024):.1f}MB so far...")
                
    except Exception as e:
        # Clean up on error
        if os.path.exists(filepath):
            os.remove(filepath)
        if isinstance(e, HTTPException):
            raise
        print(f"Upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    print(f"File saved successfully: {filepath}, size: {file_size / (1024*1024):.1f}MB")
    
    # Calculate file size in MB for database
    file_size_mb = file_size / (1024 * 1024)
    
    # Create database entry with size information
    db_document = Document(
        filename=file.filename,
        filepath=filepath,
        status=DocumentStatus.PENDING,
        file_size_mb=file_size_mb
    )
    
    # Check if file needs chunking (>40MB suggests it's a large document)
    # We'll process it through chunking pipeline for Landing.AI
    if file_size_mb > 40:
        print(f"Large file detected ({file_size_mb:.1f}MB) - will process through chunking pipeline")
        db_document.status = DocumentStatus.CHUNKING
        db_document.is_chunked = True
    
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
        file_size=file_size  # Use actual file size, not file.size
    )
    
    # If large file, trigger chunking in background
    if db_document.is_chunked:
        print(f"Triggering background chunking for document {db_document.id}")
        # Background task will handle the chunking
        background_tasks.add_task(
            process_large_document_async,
            document_id=db_document.id,
            filepath=filepath
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

@router.get("/{document_id}/parsed-fields", response_model=ParseResponse)
def get_parsed_fields(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get parsed fields for a document that has already been parsed"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.status not in [DocumentStatus.PARSED, DocumentStatus.EXTRACTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has not been parsed yet"
        )
    
    # Load parsed fields from database
    import json
    if document.parsed_fields:
        fields_data = json.loads(document.parsed_fields)
        fields = [FieldInfo(**field) for field in fields_data]
    else:
        # Fallback to OptInFormExtraction model if no saved fields
        from app.models.extraction_models import OptInFormExtraction
        fields = []
        for field_name, field_obj in OptInFormExtraction.__fields__.items():
            fields.append(FieldInfo(
                name=field_name,
                type="string" if field_obj.type_ != bool else "boolean",
                description=field_obj.field_info.description or field_name.replace('_', ' ').title(),
                required=field_obj.required
            ))
    
    return ParseResponse(
        document_id=document_id,
        fields=fields,
        markdown="",
        metadata={
            "source": "Saved parsed fields" if document.parsed_fields else "OptInFormExtraction model",
            "total_pages": document.page_count,
            "is_chunked": document.is_chunked,
            "total_chunks": document.total_chunks
        }
    )

@router.post("/{document_id}/parse", response_model=ParseResponse)
async def parse_document(
    request: Request,
    document_id: int,
    db: Session = Depends(get_db)
):
    """Parse document to detect extractable fields"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if document is ready for parsing - allow re-parsing of extracted documents
    if document.status not in [DocumentStatus.PENDING, DocumentStatus.FAILED, DocumentStatus.EXTRACTED, DocumentStatus.PARSED]:
        if document.status == DocumentStatus.CHUNKING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document is still being chunked. Please wait."
            )
        elif document.status in [DocumentStatus.EXTRACTING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document is already being processed."
            )
    
    # For chunked documents, use the first chunk for field detection
    file_to_parse = document.filepath
    if document.is_chunked:
        # Get the first chunk for field detection
        from app.models.document_chunk import DocumentChunk
        first_chunk = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).order_by(DocumentChunk.chunk_number).first()
        
        if first_chunk:
            file_to_parse = first_chunk.file_path
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No chunks found for document"
            )
    
    # Use Landing.AI service to detect fields
    from app.services.simple_landing_ai_service import SimpleLandingAIService
    service = SimpleLandingAIService()
    
    # Parse the document to get markdown and detect fields
    import asyncio
    loop = asyncio.get_event_loop()
    
    # For opt-in forms, we'll suggest the standard fields
    from app.models.extraction_models import OptInFormExtraction
    
    # Convert Pydantic model fields to FieldInfo format
    fields = []
    for field_name, field_obj in OptInFormExtraction.__fields__.items():
        fields.append(FieldInfo(
            name=field_name,
            type="string" if field_obj.type_ != bool else "boolean",
            description=field_obj.field_info.description or field_name.replace('_', ' ').title(),
            required=field_obj.required
        ))
    
    # Save parsed fields to database for later retrieval
    import json
    document.parsed_fields = json.dumps([field.dict() for field in fields])
    document.status = DocumentStatus.PARSED
    db.commit()
    
    # Return the suggested fields for user selection
    return ParseResponse(
        document_id=document_id,
        fields=fields,
        markdown="",  # We don't need to return the full markdown here
        metadata={
            "source": "OptInFormExtraction model",
            "total_pages": document.page_count,
            "is_chunked": document.is_chunked,
            "total_chunks": document.total_chunks
        }
    )

@router.post("/{document_id}/process", response_model=DocumentResponse)
async def process_document(
    request: Request,
    background_tasks: BackgroundTasks,
    document_id: int,
    extraction_request: ExtractionRequest,
    db: Session = Depends(get_db)
):
    """Process document with selected fields for extraction"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check document status - allow re-processing if already extracted or failed
    if document.status in [DocumentStatus.EXTRACTING]:
        # Return current status if already extracting
        return document
    
    # Update status to extracting
    document.status = DocumentStatus.EXTRACTING
    db.commit()
    
    # Extract selected_fields and custom_fields from the request
    selected_fields = extraction_request.selected_fields or []
    custom_fields = extraction_request.custom_fields or []
    
    # If user provided fields, use them for extraction
    if selected_fields or custom_fields:
        # Use custom extraction with selected fields
        background_tasks.add_task(
            process_document_with_fields,
            document_id=document_id,
            selected_fields=selected_fields,
            custom_fields=custom_fields
        )
    else:
        # Use the OptInFormExtraction model for default extraction
        background_tasks.add_task(
            process_document_with_model,
            document_id=document_id
        )
    
    db.refresh(document)
    return document

async def process_document_with_fields(document_id: int, selected_fields: List[str], custom_fields: List[dict] = None):
    """Process document with user-selected fields"""
    from app.core.database import SessionLocal
    from app.services.chunk_processor_optimized import OptimizedChunkProcessor
    from app.services.simple_landing_ai_service import SimpleLandingAIService
    import json
    
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Check if document is chunked
        if document.is_chunked:
            # Process chunks for large documents
            processor = OptimizedChunkProcessor(db)
            await processor.process_document_chunks(
                document=document,
                selected_fields=selected_fields,
                custom_fields=custom_fields
            )
        else:
            # Process directly for small documents
            service = SimpleLandingAIService()
            extraction_result = await service.extract_document(
                file_path=document.filepath,
                selected_fields=selected_fields,
                custom_fields=custom_fields
            )
            
            # Update document with extracted data from the ExtractionResult object
            document.extracted_data = json.dumps(extraction_result.data)
            document.extracted_md = extraction_result.markdown
            document.status = DocumentStatus.EXTRACTED
            db.commit()
        
        print(f"Successfully processed document {document_id} with selected fields")
        
    except Exception as e:
        print(f"Error processing document {document_id}: {str(e)}")
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = DocumentStatus.FAILED
            document.error_message = str(e)
            db.commit()
    finally:
        db.close()

async def process_document_with_model(document_id: int):
    """Process document with OptInFormExtraction model"""
    from app.core.database import SessionLocal
    from app.services.chunk_processor_optimized import OptimizedChunkProcessor
    from app.services.simple_landing_ai_service import SimpleLandingAIService
    from app.models.extraction_models import OptInFormExtraction
    import json
    
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Check if document is chunked
        if document.is_chunked:
            # Process chunks for large documents
            processor = OptimizedChunkProcessor(db)
            await processor.process_document_with_structured_extraction(
                document=document,
                extraction_model=OptInFormExtraction
            )
        else:
            # Process directly for small documents
            service = SimpleLandingAIService()
            extraction_result = await service.extract_with_structured_model(
                file_path=document.filepath,
                extraction_model=OptInFormExtraction
            )
            
            # Update document with extracted data from the ExtractionResult object
            if extraction_result:
                document.extracted_data = json.dumps(extraction_result.data if hasattr(extraction_result, 'data') else extraction_result)
                if hasattr(extraction_result, 'markdown'):
                    document.extracted_md = extraction_result.markdown
            else:
                document.extracted_data = json.dumps({})
            document.status = DocumentStatus.EXTRACTED
            db.commit()
        
        print(f"Successfully processed document {document_id} with OptInFormExtraction model")
        
    except Exception as e:
        print(f"Error processing document {document_id}: {str(e)}")
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = DocumentStatus.FAILED
            document.error_message = str(e)
            db.commit()
    finally:
        db.close()

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