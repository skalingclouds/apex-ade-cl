"""
Simplified Landing.AI service that focuses on getting basic extraction working.
This version provides a more user-friendly field selection based on document content.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from pydantic import BaseModel, Field, create_model
import logging
import re
import os

from app.schemas.extraction import ParseResponse, FieldInfo
from app.core.config import settings

# Import landing.ai SDK
try:
    from agentic_doc.parse import parse
    from agentic_doc.utils import viz_parsed_document
except ImportError:
    parse = None
    viz_parsed_document = None

logger = logging.getLogger(__name__)

class ExtractionResult(BaseModel):
    data: Dict[str, Any]
    markdown: str
    processed_at: datetime
    extraction_metadata: Optional[Dict[str, Any]] = None

class SimpleLandingAIService:
    def __init__(self):
        self.api_key = settings.VISION_AGENT_API_KEY
        
        # Ensure the environment variable is set for the SDK
        if self.api_key:
            os.environ['VISION_AGENT_API_KEY'] = self.api_key
            logger.info(f"SimpleLandingAIService initialized with API key")
        else:
            logger.warning("No VISION_AGENT_API_KEY found in settings")
    
    def _extract_fields_from_markdown(self, markdown: str) -> List[FieldInfo]:
        """
        Analyze the markdown to suggest meaningful fields based on content.
        This is a simple heuristic approach.
        """
        fields = []
        markdown_lower = markdown.lower()
        
        # Always include a general content field
        fields.append(FieldInfo(
            name="full_content",
            type="string",
            description="Complete document content",
            required=False
        ))
        
        # Check for specific document types and suggest relevant fields
        
        # Invoice/Financial documents
        if any(word in markdown_lower for word in ['invoice', 'bill', 'payment', 'total', 'amount', 'price']):
            fields.extend([
                FieldInfo(name="invoice_number", type="string", description="Invoice or document number", required=False),
                FieldInfo(name="date", type="string", description="Date on the document", required=False),
                FieldInfo(name="total_amount", type="string", description="Total amount or price", required=False),
                FieldInfo(name="vendor_name", type="string", description="Vendor or company name", required=False),
                FieldInfo(name="items", type="string", description="List of items or services", required=False),
            ])
        
        # Payroll/Employee documents
        if any(word in markdown_lower for word in ['payroll', 'salary', 'employee', 'wage', 'earnings']):
            fields.extend([
                FieldInfo(name="employee_name", type="string", description="Employee name(s)", required=False),
                FieldInfo(name="pay_period", type="string", description="Pay period dates", required=False),
                FieldInfo(name="gross_pay", type="string", description="Gross pay or earnings", required=False),
                FieldInfo(name="net_pay", type="string", description="Net pay amount", required=False),
                FieldInfo(name="deductions", type="string", description="Deductions and withholdings", required=False),
            ])
        
        # Contract/Legal documents
        if any(word in markdown_lower for word in ['agreement', 'contract', 'terms', 'party', 'clause']):
            fields.extend([
                FieldInfo(name="parties", type="string", description="Parties involved", required=False),
                FieldInfo(name="effective_date", type="string", description="Effective date", required=False),
                FieldInfo(name="terms", type="string", description="Key terms and conditions", required=False),
                FieldInfo(name="signatures", type="string", description="Signature information", required=False),
            ])
        
        # Report/Analysis documents
        if any(word in markdown_lower for word in ['report', 'analysis', 'summary', 'findings', 'conclusion']):
            fields.extend([
                FieldInfo(name="title", type="string", description="Report title", required=False),
                FieldInfo(name="summary", type="string", description="Executive summary", required=False),
                FieldInfo(name="key_findings", type="string", description="Key findings or results", required=False),
                FieldInfo(name="recommendations", type="string", description="Recommendations", required=False),
            ])
        
        # Forms
        if any(word in markdown_lower for word in ['form', 'application', 'registration', 'name:', 'address:', 'phone:']):
            fields.extend([
                FieldInfo(name="applicant_name", type="string", description="Name of applicant", required=False),
                FieldInfo(name="contact_info", type="string", description="Contact information", required=False),
                FieldInfo(name="address", type="string", description="Address", required=False),
                FieldInfo(name="form_date", type="string", description="Form date", required=False),
            ])
        
        # Tables (if markdown contains table syntax)
        if '<table>' in markdown or '|' in markdown[:1000]:  # Check for table markers
            fields.append(FieldInfo(
                name="table_data",
                type="string",
                description="Extracted table information",
                required=False
            ))
        
        # Generic fields as fallback
        if len(fields) < 5:
            fields.extend([
                FieldInfo(name="document_title", type="string", description="Document title or heading", required=False),
                FieldInfo(name="key_information", type="string", description="Key information from document", required=False),
                FieldInfo(name="dates", type="string", description="Important dates", required=False),
                FieldInfo(name="numbers", type="string", description="Important numbers or amounts", required=False),
            ])
        
        # Remove duplicates based on field name
        seen = set()
        unique_fields = []
        for field in fields:
            if field.name not in seen:
                seen.add(field.name)
                unique_fields.append(field)
        
        return unique_fields[:15]  # Limit to 15 fields for UI clarity
    
    async def parse_document(self, file_path: str) -> ParseResponse:
        """
        Parse document to get markdown and suggest extraction fields.
        """
        logger.info(f"Parsing document: {file_path}")
        
        if parse is None:
            # Mock response for development
            mock_markdown = "# Mock Document\n\nThis is a mock parsed document."
            return ParseResponse(
                fields=self._extract_fields_from_markdown(mock_markdown),
                document_type="mock",
                confidence=0.95,
                markdown=mock_markdown
            )
        
        try:
            # Run parse
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
            markdown_content = getattr(parsed_doc, 'markdown', '')
            
            logger.info(f"Parse successful. Markdown length: {len(markdown_content)}")
            
            # Suggest fields based on actual content
            suggested_fields = self._extract_fields_from_markdown(markdown_content)
            
            return ParseResponse(
                fields=suggested_fields,
                document_type=getattr(parsed_doc, 'doc_type', 'document'),
                confidence=0.9,
                markdown=markdown_content
            )
            
        except Exception as e:
            logger.error(f"Parse failed: {str(e)}", exc_info=True)
            raise Exception(f"Failed to parse document: {str(e)}")
    
    async def extract_document(
        self, 
        file_path: str,
        schema_model: type[BaseModel],
        selected_fields: List[str]
    ) -> ExtractionResult:
        """
        Extract data from document using provided schema.
        """
        logger.info(f"Extracting from document: {file_path}")
        logger.info(f"Selected fields: {selected_fields}")
        
        if parse is None:
            # Mock response with chunk telemetry for development
            mock_data = {field: f"Sample {field} value" for field in selected_fields}
            
            # Add mock chunks with bounding boxes
            mock_chunks = [
                {
                    'id': '0',
                    'text': 'Sample chunk text 1',
                    'page': 1,
                    'bbox': [100, 100, 400, 200]  # [x1, y1, x2, y2]
                },
                {
                    'id': '1',
                    'text': 'Sample chunk text 2',
                    'page': 1,
                    'bbox': [100, 250, 400, 350]
                }
            ]
            
            mock_data['chunks'] = mock_chunks
            
            return ExtractionResult(
                data=mock_data,
                markdown="# Mock Extraction\n\nThis is mock extracted content.",
                processed_at=datetime.now()
            )
        
        try:
            # Run extraction with the schema
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: parse(
                    documents=[file_path],
                    extraction_model=schema_model
                )
            )
            
            if not result or len(result) == 0:
                # If extraction fails, still return the markdown
                result = await loop.run_in_executor(
                    None,
                    lambda: parse(
                        documents=[file_path],
                        include_marginalia=True,
                        include_metadata_in_markdown=True
                    )
                )
                
                if result and len(result) > 0:
                    markdown_content = getattr(result[0], 'markdown', '')
                    empty_data = {field: None for field in selected_fields}
                    return ExtractionResult(
                        data=empty_data,
                        markdown=markdown_content,
                        processed_at=datetime.now()
                    )
                
                raise Exception("No results from parse")
            
            parsed_doc = result[0]
            
            # Get extracted data if available
            if hasattr(parsed_doc, 'extraction') and parsed_doc.extraction:
                extracted_data = parsed_doc.extraction.model_dump()
                filtered_data = {
                    field: extracted_data.get(field, None) 
                    for field in selected_fields
                }
            else:
                filtered_data = {field: None for field in selected_fields}
            
            # Always try to get markdown
            markdown_content = getattr(parsed_doc, 'markdown', '')
            
            # Extract chunk telemetry with bounding boxes if available
            chunks_with_telemetry = []
            if hasattr(parsed_doc, 'chunks'):
                for idx, chunk in enumerate(parsed_doc.chunks):
                    chunk_data = {
                        'id': str(idx),
                        'text': getattr(chunk, 'text', ''),
                        'page': getattr(chunk, 'page', 1)
                    }
                    
                    # Try to get bounding box information
                    if hasattr(chunk, 'bbox'):
                        chunk_data['bbox'] = chunk.bbox
                    elif hasattr(chunk, 'bounding_box'):
                        chunk_data['bbox'] = chunk.bounding_box
                    elif hasattr(chunk, 'coordinates'):
                        # Convert coordinates to bbox format [x1, y1, x2, y2]
                        coords = chunk.coordinates
                        if isinstance(coords, dict):
                            chunk_data['bbox'] = [
                                coords.get('x', 0),
                                coords.get('y', 0),
                                coords.get('x', 0) + coords.get('width', 100),
                                coords.get('y', 0) + coords.get('height', 100)
                            ]
                    
                    chunks_with_telemetry.append(chunk_data)
            
            # Include chunks in the extraction result
            result_data = {
                **filtered_data,
                'chunks': chunks_with_telemetry
            }
            
            return ExtractionResult(
                data=result_data,
                markdown=markdown_content,
                processed_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Extraction error: {str(e)}", exc_info=True)
            
            # Try to at least get markdown
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
                
                markdown_content = ""
                if result and len(result) > 0:
                    markdown_content = getattr(result[0], 'markdown', '')
                
                empty_data = {field: None for field in selected_fields}
                return ExtractionResult(
                    data=empty_data,
                    markdown=markdown_content or f"Extraction failed: {str(e)}",
                    processed_at=datetime.now()
                )
            except:
                empty_data = {field: None for field in selected_fields}
                return ExtractionResult(
                    data=empty_data,
                    markdown=f"Extraction failed: {str(e)}",
                    processed_at=datetime.now()
                )