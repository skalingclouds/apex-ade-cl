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
    
    # Parse extracted data
    data = json.loads(document.extracted_data)
    
    # Create CSV in memory
    output = io.StringIO()
    if isinstance(data, dict):
        # Single record
        writer = csv.DictWriter(output, fieldnames=data.keys())
        writer.writeheader()
        writer.writerow(data)
    elif isinstance(data, list) and len(data) > 0:
        # Multiple records
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid data format for CSV export"
        )
    
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
    
    # Create markdown content with metadata
    content = f"# {document.filename}\n\n"
    content += f"**Extracted on:** {document.processed_at}\n"
    content += f"**Status:** {document.status}\n\n"
    content += "---\n\n"
    content += document.extracted_md
    
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
    
    return {
        "markdown": document.extracted_md,
        "processed_at": document.processed_at,
        "status": document.status
    }