from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from starlette.requests import Request
from sqlalchemy.orm import Session
import json
from typing import Dict, Any, Optional
from pydantic import create_model, Field
import logging

from app.core.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.extraction_schema import ExtractionSchema
from app.models.custom_field import CustomField
from app.schemas.extraction import ParseResponse, ExtractionRequest, ExtractionResponse, FieldInfo
from app.services.landing_ai_service import LandingAIService
from app.services.simple_landing_ai_service import SimpleLandingAIService
from app.services.audit_service import AuditService
from app.services.analytics_service import AnalyticsService
from app.core.error_handlers import (
    DocumentNotFoundError, SchemaValidationError, 
    LandingAIError, ExtractionError
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/{document_id}/parse", response_model=ParseResponse)
async def parse_document(
    request: Request,
    background_tasks: BackgroundTasks,
    document_id: int,
    db: Session = Depends(get_db)
):
    """Parse document to identify extractable fields"""
    # Debug schema loading
    logger.info(f"ParseResponse schema fields: {ParseResponse.__fields__}")
    logger.info(f"ParseResponse schema: {ParseResponse.schema()}")
    
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise DocumentNotFoundError(document_id)
    
    if document.status != DocumentStatus.PENDING:
        raise ExtractionError(
            f"Document is in {document.status} status and cannot be parsed. Only pending documents can be parsed.",
            "INVALID_DOCUMENT_STATUS"
        )
    
    # Update status
    document.status = DocumentStatus.PARSING
    db.commit()
    
    try:
        # Parse document using simplified landing.ai SDK service
        service = SimpleLandingAIService()
        parse_result = await service.parse_document(document.filepath)
        
        # Update status and save markdown if available
        old_status = document.status
        document.status = DocumentStatus.PARSED
        # Save markdown from parse result
        if parse_result.markdown:
            document.extracted_md = parse_result.markdown
        db.commit()
        
        # Analytics event logging
        analytics_service = AnalyticsService(db, request, background_tasks)
        analytics_service.log_document_status_change(
            document_id=document_id,
            old_status=old_status.value,
            new_status=DocumentStatus.PARSED.value
        )
        
        return parse_result
        
    except LandingAIError:
        raise  # Re-raise Landing AI errors
    except Exception as e:
        document.status = DocumentStatus.FAILED
        document.error_message = str(e)
        db.commit()
        logger.error(f"Parse failed for document {document_id}: {str(e)}")
        
        # Check if it's a Landing AI related error
        if "landing" in str(e).lower() or "api" in str(e).lower():
            raise LandingAIError(f"Failed to connect to Landing AI service: {str(e)}")
        else:
            raise ExtractionError(f"Failed to parse document: {str(e)}")

@router.post("/{document_id}/extract", response_model=ExtractionResponse)
async def extract_document_data(
    request: Request,
    document_id: int,
    extraction_request: ExtractionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Extract data from document using selected fields"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise DocumentNotFoundError(document_id)
    
    if document.status not in [DocumentStatus.PARSED, DocumentStatus.EXTRACTED, DocumentStatus.REJECTED]:
        raise ExtractionError(
            f"Document is in {document.status} status. Document must be parsed before extraction.",
            "INVALID_DOCUMENT_STATUS"
        )
    
    # Validate that at least one field is selected
    if not extraction_request.selected_fields:
        raise SchemaValidationError("At least one field must be selected for extraction")
    
    # Update status
    document.status = DocumentStatus.EXTRACTING
    db.commit()
    
    # Create dynamic Pydantic model based on selected fields and custom fields
    # Since Landing.AI will try to extract whatever it can, make all fields optional strings
    from typing import Optional
    from pydantic import Field
    
    field_definitions = {}
    
    # Add custom fields to the extraction model and save them to database
    if extraction_request.custom_fields:
        for custom_field in extraction_request.custom_fields:
            field_definitions[custom_field.name] = (
                Optional[str], 
                Field(None, description=custom_field.description or f"Custom field: {custom_field.name}")
            )
            
            # Save or update custom field in database for future reuse
            existing_field = db.query(CustomField).filter(
                CustomField.name == custom_field.name
            ).first()
            
            if existing_field:
                existing_field.usage_count += 1
                existing_field.description = custom_field.description or existing_field.description
            else:
                new_custom_field = CustomField(
                    name=custom_field.name,
                    type=custom_field.type,
                    description=custom_field.description,
                    usage_count=1
                )
                db.add(new_custom_field)
        
        db.commit()
    
    # Add regular selected fields
    for field_name in extraction_request.selected_fields:
        # Skip if already added as custom field
        if field_name not in field_definitions:
            field_definitions[field_name] = (Optional[str], Field(None, description=f"Field: {field_name}"))
    
    DynamicModel = create_model('DynamicExtractionModel', **field_definitions)
    
    # Save extraction schema
    # Convert field_definitions to JSON-serializable format
    schema_dict = {}
    for field_name, (field_type, default) in field_definitions.items():
        # Handle Optional types which don't have __name__
        type_name = "string"  # Default to string since we're using Optional[str]
        schema_dict[field_name] = {
            'type': type_name,
            'required': False  # All fields are optional
        }
    
    schema_entry = ExtractionSchema(
        document_id=document_id,
        schema_json=json.dumps(schema_dict),
        selected_fields=json.dumps(extraction_request.selected_fields)
    )
    db.add(schema_entry)
    db.commit()
    
    try:
        # Extract data using simplified landing.ai SDK service
        service = SimpleLandingAIService()
        extraction_result = await service.extract_document(
            document.filepath,
            DynamicModel,
            extraction_request.selected_fields
        )
        
        # Update document with results
        old_status = document.status
        document.status = DocumentStatus.EXTRACTED
        document.extracted_data = json.dumps(extraction_result.data)
        document.extracted_md = extraction_result.markdown
        document.processed_at = extraction_result.processed_at
        db.commit()
        
        # Audit log successful extraction
        audit_service = AuditService(db, request)
        audit_service.log_extraction(
            document_id=document_id,
            selected_fields=extraction_request.selected_fields,
            success=True
        )
        
        # Analytics event logging
        analytics_service = AnalyticsService(db, request, background_tasks)
        analytics_service.log_document_status_change(
            document_id=document_id,
            old_status=old_status.value,
            new_status=DocumentStatus.EXTRACTED.value
        )
        
        return ExtractionResponse(
            success=True,
            extracted_data=extraction_result.data,
            markdown=extraction_result.markdown
        )
        
    except (LandingAIError, SchemaValidationError, ExtractionError):
        raise  # Re-raise our custom errors
    except Exception as e:
        document.status = DocumentStatus.FAILED
        document.error_message = str(e)
        db.commit()
        logger.error(f"Extraction failed for document {document_id}: {str(e)}")
        
        # Audit log failed extraction
        audit_service = AuditService(db, request)
        audit_service.log_extraction(
            document_id=document_id,
            selected_fields=extraction_request.selected_fields,
            success=False,
            error_message=str(e)
        )
        
        # Check the type of error
        if "validation" in str(e).lower():
            raise SchemaValidationError(f"Schema validation failed: {str(e)}")
        elif "landing" in str(e).lower() or "api" in str(e).lower():
            raise LandingAIError(f"Landing AI service error: {str(e)}")
        else:
            raise ExtractionError(f"Extraction failed: {str(e)}")

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

@router.post("/{document_id}/retry", response_model=ExtractionResponse)
async def retry_extraction(
    request: Request,
    background_tasks: BackgroundTasks,
    document_id: int,
    db: Session = Depends(get_db)
):
    """Retry extraction for a failed document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise DocumentNotFoundError(document_id)
    
    if document.status != DocumentStatus.FAILED:
        raise ExtractionError(
            f"Document is in {document.status} status. Only failed documents can be retried.",
            "INVALID_RETRY_STATUS"
        )
    
    # Get the last extraction schema
    schema = db.query(ExtractionSchema).filter(
        ExtractionSchema.document_id == document_id
    ).order_by(ExtractionSchema.created_at.desc()).first()
    
    if not schema:
        # If no schema exists, retry parsing first
        document.status = DocumentStatus.PENDING
        db.commit()
        raise ExtractionError(
            "No previous extraction attempt found. Please parse the document first.",
            "NO_SCHEMA_FOUND"
        )
    
    # Retry with the same selected fields
    selected_fields = json.loads(schema.selected_fields)
    extraction_req = ExtractionRequest(selected_fields=selected_fields)
    
    # Clear error and retry
    document.error_message = None
    db.commit()
    
    # Log extraction retry attempt
    analytics_service = AnalyticsService(db, request, background_tasks)
    analytics_service.log_extraction_retry(
        document_id=document_id,
        attempt=1,  # Could track this better in the future
        error_message=None
    )
    
    return await extract_document_data(document_id, extraction_req, background_tasks, request, db)

@router.get("/custom-fields")
def get_custom_fields(
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Get frequently used custom fields for suggestions"""
    custom_fields = db.query(CustomField).filter(
        CustomField.is_active == True
    ).order_by(CustomField.usage_count.desc()).limit(limit).all()
    
    return {
        "custom_fields": [
            {
                "name": field.name,
                "type": field.type,
                "description": field.description,
                "usage_count": field.usage_count,
                "required": False
            }
            for field in custom_fields
        ]
    }