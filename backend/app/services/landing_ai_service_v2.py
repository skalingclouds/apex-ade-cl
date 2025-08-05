from typing import List, Dict, Any, Type, Optional
from datetime import datetime
from pathlib import Path
import asyncio
from pydantic import BaseModel, Field, create_model
import logging

from app.schemas.extraction import ParseResponse, FieldInfo
from app.core.config import settings

# Import landing.ai SDK
try:
    from agentic_doc.parse import parse
    from agentic_doc.utils import viz_parsed_document
except ImportError:
    # Fallback for development without the SDK
    parse = None
    viz_parsed_document = None

logger = logging.getLogger(__name__)

class ExtractionResult(BaseModel):
    data: Dict[str, Any]
    markdown: str
    processed_at: datetime
    extraction_metadata: Optional[Dict[str, Any]] = None

class LandingAIService:
    def __init__(self):
        self.api_key = settings.LANDING_AI_API_KEY
        logger.info(f"LandingAIService initialized with API key: {self.api_key[:10]}...")
    
    async def parse_document(self, file_path: str) -> ParseResponse:
        """
        Parse document to get markdown and identify potential fields.
        This is step 1 - just parsing without extraction.
        """
        logger.info(f"Starting document parse for: {file_path}")
        
        if parse is None:
            # Mock response for development
            logger.warning("Landing.AI SDK not available, returning mock response")
            return ParseResponse(
                fields=[
                    FieldInfo(name="invoice_number", type="string", description="Invoice number"),
                    FieldInfo(name="date", type="string", description="Date"),
                    FieldInfo(name="total", type="number", description="Total amount"),
                    FieldInfo(name="vendor", type="string", description="Vendor name"),
                ],
                document_type="invoice",
                confidence=0.95,
                markdown="# Mock Document\n\nThis is a mock parsed document."
            )
        
        try:
            # Run parse in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: parse(
                    documents=[file_path],
                    include_marginalia=True,
                    include_metadata_in_markdown=True
                )
            )
            
            if not result or len(result) == 0:
                raise Exception("No results returned from parse")
            
            parsed_doc = result[0]
            
            # Log what we got
            logger.info(f"Parse successful. Document type: {getattr(parsed_doc, 'doc_type', 'unknown')}")
            logger.info(f"Has markdown: {hasattr(parsed_doc, 'markdown')}")
            logger.info(f"Markdown length: {len(getattr(parsed_doc, 'markdown', ''))}")
            
            # Get the markdown content
            markdown_content = getattr(parsed_doc, 'markdown', '')
            
            # Generate suggested fields based on common document patterns
            # For now, we'll provide a standard set that users can customize
            suggested_fields = [
                FieldInfo(name="custom_field_1", type="string", description="Custom text field 1", required=False),
                FieldInfo(name="custom_field_2", type="string", description="Custom text field 2", required=False),
                FieldInfo(name="custom_field_3", type="string", description="Custom text field 3", required=False),
                FieldInfo(name="custom_field_4", type="number", description="Custom numeric field", required=False),
                FieldInfo(name="custom_field_5", type="string", description="Custom text field 5", required=False),
                FieldInfo(name="date", type="string", description="Date field", required=False),
                FieldInfo(name="amount", type="number", description="Amount or total", required=False),
                FieldInfo(name="name", type="string", description="Name or title", required=False),
                FieldInfo(name="description", type="string", description="Description or notes", required=False),
                FieldInfo(name="reference", type="string", description="Reference number or ID", required=False),
            ]
            
            # Return the parse response with markdown
            return ParseResponse(
                fields=suggested_fields,
                document_type=getattr(parsed_doc, 'doc_type', 'document'),
                confidence=0.9,
                markdown=markdown_content
            )
            
        except Exception as e:
            logger.error(f"Parse failed: {str(e)}", exc_info=True)
            raise Exception(f"Failed to parse document: {str(e)}")
    
    async def extract_document_with_schema(
        self, 
        file_path: str,
        selected_fields: List[str],
        field_descriptions: Optional[Dict[str, str]] = None
    ) -> ExtractionResult:
        """
        Extract data from document using selected fields.
        This is step 2 - extraction with a dynamic schema.
        """
        logger.info(f"Starting extraction for: {file_path}")
        logger.info(f"Selected fields: {selected_fields}")
        
        if parse is None:
            # Mock response for development
            mock_data = {
                field: f"Sample {field} value" for field in selected_fields
            }
            return ExtractionResult(
                data=mock_data,
                markdown=f"# Extracted Data\n\n" + "\n".join([f"**{k}**: {v}" for k, v in mock_data.items()]),
                processed_at=datetime.now()
            )
        
        try:
            # Create dynamic Pydantic model based on selected fields
            field_definitions = {}
            for field_name in selected_fields:
                # Get description if provided
                desc = field_descriptions.get(field_name, f"Field: {field_name}") if field_descriptions else f"Field: {field_name}"
                # Make all fields optional strings by default
                # Landing.AI will try to extract whatever it can find
                field_definitions[field_name] = (Optional[str], Field(None, description=desc))
            
            # Create the dynamic model
            DynamicExtractionModel = create_model('DynamicExtractionModel', **field_definitions)
            
            logger.info(f"Created dynamic model with fields: {list(field_definitions.keys())}")
            
            # Run extraction with the dynamic schema
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: parse(
                    documents=[file_path],
                    extraction_model=DynamicExtractionModel
                )
            )
            
            if not result or len(result) == 0:
                raise Exception("No results returned from extraction")
            
            parsed_doc = result[0]
            
            # Check if extraction was successful
            if hasattr(parsed_doc, 'extraction') and parsed_doc.extraction:
                logger.info("Extraction successful, processing results")
                
                # Get the extracted data
                extracted_data = parsed_doc.extraction.model_dump()
                
                # Get extraction metadata if available
                extraction_metadata = None
                if hasattr(parsed_doc, 'extraction_metadata'):
                    try:
                        extraction_metadata = parsed_doc.extraction_metadata.model_dump()
                    except:
                        extraction_metadata = str(parsed_doc.extraction_metadata)
                
                # Get markdown (might be available even with extraction)
                markdown_content = getattr(parsed_doc, 'markdown', '')
                
                logger.info(f"Extracted data: {extracted_data}")
                
                return ExtractionResult(
                    data=extracted_data,
                    markdown=markdown_content,
                    processed_at=datetime.now(),
                    extraction_metadata=extraction_metadata
                )
            else:
                # No extraction attribute, return empty values for requested fields
                logger.warning("No extraction results found, returning empty fields")
                empty_data = {field: None for field in selected_fields}
                
                return ExtractionResult(
                    data=empty_data,
                    markdown=getattr(parsed_doc, 'markdown', ''),
                    processed_at=datetime.now()
                )
                
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}", exc_info=True)
            # Return empty data rather than failing completely
            empty_data = {field: None for field in selected_fields}
            return ExtractionResult(
                data=empty_data,
                markdown=f"Extraction failed: {str(e)}",
                processed_at=datetime.now()
            )
    
    async def simple_parse_for_markdown(self, file_path: str) -> str:
        """
        Simple parse just to get markdown content.
        Used when we just want the document text without extraction.
        """
        logger.info(f"Simple parse for markdown: {file_path}")
        
        if parse is None:
            return "# Mock Document\n\nLanding.AI SDK not available."
        
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: parse(
                    documents=[file_path],
                    include_marginalia=True,
                    include_metadata_in_markdown=True
                )
            )
            
            if result and len(result) > 0:
                return getattr(result[0], 'markdown', '')
            
            return ""
            
        except Exception as e:
            logger.error(f"Simple parse failed: {str(e)}")
            return f"Failed to parse document: {str(e)}"