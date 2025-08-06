from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from starlette.requests import Request
from sqlalchemy.orm import Session
import json
import csv
import io
import logging

from app.core.database import get_db
from app.models.document import Document, DocumentStatus
from app.services.audit_service import AuditService
from app.services.analytics_service import AnalyticsService
from app.utils.enhanced_markdown_processor import LandingAIMarkdownProcessor

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/{document_id}/export/csv")
def export_as_csv(
    request: Request,
    document_id: int,
    db: Session = Depends(get_db)
):
    """Export extracted data as CSV"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if document is in a valid state for export
    if document.status not in [DocumentStatus.EXTRACTED, DocumentStatus.APPROVED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document must be extracted or approved for export. Current status: {document.status}"
        )
    
    if not document.extracted_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No extracted data available for export"
        )
    
    # Convert markdown and extracted data to CSV format
    csv_string = LandingAIMarkdownProcessor.extract_clean_csv_data(
        markdown=document.extracted_md,
        extracted_data=document.extracted_data
    )
    
    if not csv_string:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data available for CSV export"
        )
    
    # CSV is already formatted, just create the output
    output = io.StringIO(csv_string)
    output.seek(0)
    
    # Log the export action
    try:
        audit_service = AuditService(db, request)
        audit_service.log_document_access(
            document_id=document_id,
            action="export_csv"
        )
    except Exception as e:
        logger.warning(f"Failed to log export audit: {str(e)}")
    
    # Analytics event logging (synchronous since no BackgroundTasks in export)
    try:
        analytics_service = AnalyticsService(db, request)
        analytics_service.log_document_export(
            document_id=document_id,
            export_format="csv",
            file_size=len(output.getvalue())
        )
    except Exception as e:
        logger.warning(f"Failed to log export analytics: {str(e)}")
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={document.filename.replace('.pdf', '')}_export.csv"
        }
    )

@router.get("/{document_id}/export/markdown")
def export_as_markdown(
    request: Request,
    document_id: int,
    db: Session = Depends(get_db)
):
    """Export extracted content as Markdown"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if document is in a valid state for export
    if document.status not in [DocumentStatus.EXTRACTED, DocumentStatus.APPROVED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document must be extracted or approved for export. Current status: {document.status}"
        )
    
    if not document.extracted_md:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No extracted markdown available for export"
        )
    
    # Format markdown for clean export
    clean_markdown = LandingAIMarkdownProcessor.format_for_markdown_export(document.extracted_md)
    
    # Create markdown content with metadata
    content = f"# {document.filename}\n\n"
    content += f"**Extracted on:** {document.processed_at}\n"
    content += f"**Status:** {document.status}\n\n"
    content += "---\n\n"
    content += clean_markdown
    
    # Log the export action
    try:
        audit_service = AuditService(db, request)
        audit_service.log_document_access(
            document_id=document_id,
            action="export_markdown"
        )
    except Exception as e:
        logger.warning(f"Failed to log export audit: {str(e)}")
    
    # Analytics event logging
    try:
        analytics_service = AnalyticsService(db, request)
        analytics_service.log_document_export(
            document_id=document_id,
            export_format="markdown",
            file_size=len(content.encode())
        )
    except Exception as e:
        logger.warning(f"Failed to log export analytics: {str(e)}")
    
    return StreamingResponse(
        io.BytesIO(content.encode()),
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename={document.filename.replace('.pdf', '')}_export.md"
        }
    )

@router.get("/{document_id}/export/text")
def export_as_text(
    request: Request,
    document_id: int,
    db: Session = Depends(get_db)
):
    """Export extracted content as plain text (no markdown formatting)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if document is in a valid state for export
    if document.status not in [DocumentStatus.EXTRACTED, DocumentStatus.APPROVED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document must be extracted or approved for export. Current status: {document.status}"
        )
    
    if not document.extracted_md:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No extracted content available for export"
        )
    
    # Convert markdown to plain text
    plain_text = LandingAIMarkdownProcessor.extract_plain_text(document.extracted_md)
    
    # Create text content with metadata
    content = f"{document.filename}\n\n"
    content += f"Extracted on: {document.processed_at}\n"
    content += f"Status: {document.status}\n\n"
    content += "-" * 50 + "\n\n"
    content += plain_text
    
    # Log the export action
    try:
        audit_service = AuditService(db, request)
        audit_service.log_document_access(
            document_id=document_id,
            action="export_text"
        )
    except Exception as e:
        logger.warning(f"Failed to log export audit: {str(e)}")
    
    # Analytics event logging
    try:
        analytics_service = AnalyticsService(db, request)
        analytics_service.log_document_export(
            document_id=document_id,
            export_format="text",
            file_size=len(content.encode())
        )
    except Exception as e:
        logger.warning(f"Failed to log export analytics: {str(e)}")
    
    return StreamingResponse(
        io.BytesIO(content.encode()),
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename={document.filename.replace('.pdf', '')}_export.txt"
        }
    )

@router.get("/{document_id}/pdf")
async def get_original_pdf(
    request: Request,
    document_id: int,
    db: Session = Depends(get_db)
):
    """Stream the original PDF file"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Verify file exists
    try:
        with open(document.filepath, 'rb') as f:
            pass  # Just checking if file exists
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Original PDF file not found on server"
        )
    except Exception as e:
        logger.error(f"Error accessing PDF file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error accessing PDF file"
        )
    
    # Log the access
    try:
        audit_service = AuditService(db, request)
        audit_service.log_document_access(
            document_id=document_id,
            action="download_pdf"
        )
    except Exception as e:
        logger.warning(f"Failed to log PDF access audit: {str(e)}")
    
    def iterfile():
        with open(document.filepath, 'rb') as f:
            yield from f
    
    return StreamingResponse(
        iterfile(),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename={document.filename}"
        }
    )

@router.get("/{document_id}/markdown")
def get_extracted_markdown(
    request: Request,
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get the extracted markdown content"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if not document.extracted_md:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No extracted markdown available"
        )
    
    # Log the access
    try:
        audit_service = AuditService(db, request)
        audit_service.log_document_access(
            document_id=document_id,
            action="view_markdown"
        )
    except Exception as e:
        logger.warning(f"Failed to log markdown view audit: {str(e)}")
    
    # Clean the markdown before sending to frontend
    cleaned_markdown = LandingAIMarkdownProcessor.clean_markdown_for_display(document.extracted_md)
    
    return {
        "markdown": cleaned_markdown,
        "processed_at": document.processed_at,
        "status": document.status
    }