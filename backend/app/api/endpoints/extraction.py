from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
import json
from typing import Dict, Any
from pydantic import create_model

from app.core.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.extraction_schema import ExtractionSchema
from app.schemas.extraction import ParseResponse, ExtractionRequest, ExtractionResponse, FieldInfo
from app.services.landing_ai_service import LandingAIService

router = APIRouter()

@router.post("/{document_id}/parse", response_model=ParseResponse)
async def parse_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Parse document to identify extractable fields"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.status != DocumentStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has already been processed"
        )
    
    # Update status
    document.status = DocumentStatus.PARSING
    db.commit()
    
    try:
        # Parse document using landing.ai SDK
        service = LandingAIService()
        parse_result = await service.parse_document(document.filepath)
        
        # Update status
        document.status = DocumentStatus.PARSED
        db.commit()
        
        return parse_result
        
    except Exception as e:
        document.status = DocumentStatus.FAILED
        document.error_message = str(e)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse document: {str(e)}"
        )

@router.post("/{document_id}/extract", response_model=ExtractionResponse)
async def extract_document_data(
    document_id: int,
    extraction_request: ExtractionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Extract data from document using selected fields"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.status not in [DocumentStatus.PARSED, DocumentStatus.EXTRACTED, DocumentStatus.REJECTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document must be parsed before extraction"
        )
    
    # Update status
    document.status = DocumentStatus.EXTRACTING
    db.commit()
    
    # Create dynamic Pydantic model based on selected fields
    field_definitions = {}
    for field_name in extraction_request.selected_fields:
        field_definitions[field_name] = (str, ...)  # Default to string type
    
    DynamicModel = create_model('DynamicExtractionModel', **field_definitions)
    
    # Save extraction schema
    schema_entry = ExtractionSchema(
        document_id=document_id,
        schema_json=json.dumps(field_definitions),
        selected_fields=json.dumps(extraction_request.selected_fields)
    )
    db.add(schema_entry)
    db.commit()
    
    try:
        # Extract data using landing.ai SDK
        service = LandingAIService()
        extraction_result = await service.extract_document(
            document.filepath,
            DynamicModel,
            extraction_request.selected_fields
        )
        
        # Update document with results
        document.status = DocumentStatus.EXTRACTED
        document.extracted_data = json.dumps(extraction_result.data)
        document.extracted_md = extraction_result.markdown
        document.processed_at = extraction_result.processed_at
        db.commit()
        
        return ExtractionResponse(
            success=True,
            extracted_data=extraction_result.data,
            markdown=extraction_result.markdown
        )
        
    except Exception as e:
        document.status = DocumentStatus.FAILED
        document.error_message = str(e)
        db.commit()
        return ExtractionResponse(
            success=False,
            error=str(e)
        )

@router.get("/{document_id}/schema")
def get_extraction_schema(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get the extraction schema used for a document"""
    schema = db.query(ExtractionSchema).filter(
        ExtractionSchema.document_id == document_id
    ).order_by(ExtractionSchema.created_at.desc()).first()
    
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No extraction schema found for this document"
        )
    
    return {
        "schema": json.loads(schema.schema_json),
        "selected_fields": json.loads(schema.selected_fields),
        "created_at": schema.created_at
    }