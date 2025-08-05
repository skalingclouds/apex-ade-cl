from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import csv
import io

from app.core.database import get_db
from app.models.document import Document, DocumentStatus

router = APIRouter()

@router.get("/{document_id}/export/csv")
def export_as_csv(
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
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode()),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={document.filename.replace('.pdf', '')}_export.csv"
        }
    )

@router.get("/{document_id}/export/markdown")
def export_as_markdown(
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
    
    return StreamingResponse(
        io.BytesIO(content.encode()),
        media_type="text/markdown",
        headers={
            "Content-Disposition": f"attachment; filename={document.filename.replace('.pdf', '')}_export.md"
        }
    )

@router.get("/{document_id}/pdf")
async def get_original_pdf(
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
    
    return {
        "markdown": document.extracted_md,
        "processed_at": document.processed_at
    }