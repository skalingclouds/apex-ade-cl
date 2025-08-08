"""
Simplified Landing.AI service that focuses on getting basic extraction working.
This version provides dynamic field selection based on actual document content using AI analysis.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from pydantic import BaseModel, Field, create_model
import logging
import re
import os
import json
import requests

from app.schemas.extraction import ParseResponse, FieldInfo
from app.core.config import settings

# Import landing.ai SDK
try:
    from agentic_doc.parse import parse
    from agentic_doc.config import ParseConfig
    from agentic_doc.utils import viz_parsed_document
except ImportError:
    parse = None
    ParseConfig = None
    viz_parsed_document = None

# Import OpenAI for dynamic field generation
try:
    import openai
    from openai import OpenAI
except ImportError:
    openai = None
    OpenAI = None

logger = logging.getLogger(__name__)

class ExtractionResult(BaseModel):
    data: Dict[str, Any]
    markdown: str
    processed_at: datetime
    extraction_metadata: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None  # For extraction method tracking

class SimpleLandingAIService:
    def __init__(self):
        self.api_key = settings.VISION_AGENT_API_KEY
        self.api_endpoint = "https://api.va.landing.ai/v1/tools/agentic-document-analysis"
        
        # Ensure the environment variable is set for the SDK
        if self.api_key:
            os.environ['VISION_AGENT_API_KEY'] = self.api_key
            logger.info(f"SimpleLandingAIService initialized with API key")
        else:
            logger.warning("No VISION_AGENT_API_KEY found in settings")
    
    def _extract_fields_from_markdown(self, markdown: str) -> List[FieldInfo]:
        """
        Use AI to analyze the document content and suggest relevant extraction fields.
        This provides truly dynamic field generation based on actual document content.
        """
        # Try AI-based field generation first
        if OpenAI and settings.OPENAI_API_KEY:
            try:
                return self._extract_fields_using_ai(markdown)
            except Exception as e:
                logger.warning(f"AI field generation failed, using fallback: {str(e)}")
        
        # Fallback to pattern-based field generation
        return self._extract_fields_fallback(markdown)
    
    def _extract_fields_using_ai(self, markdown: str) -> List[FieldInfo]:
        """
        Use OpenAI to analyze document and suggest relevant fields.
        """
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Truncate markdown if too long (keep first 3000 chars for analysis)
        markdown_sample = markdown[:3000] if len(markdown) > 3000 else markdown
        
        prompt = f"""Analyze this document content and suggest relevant fields to extract. 
        Return a JSON array of field suggestions. Each field should have:
        - name: snake_case field name (e.g., 'invoice_number', 'total_amount')
        - type: always 'string' for compatibility
        - description: brief description of what this field contains
        - required: always false
        
        Analyze the actual content and structure to suggest fields that are actually present in the document.
        Limit to 12-15 most relevant fields. Focus on extractable data like names, dates, amounts, IDs, addresses, etc.
        
        Document content:
        {markdown_sample}
        
        Return ONLY a JSON array, no other text. Example format:
        [
            {{"name": "invoice_number", "type": "string", "description": "Invoice or reference number", "required": false}},
            {{"name": "date", "type": "string", "description": "Document date", "required": false}}
        ]
        """
        
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL or "gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a document analysis expert. Analyze documents and suggest relevant fields to extract based on the actual content present."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Lower temperature for more consistent field suggestions
            max_tokens=1000
        )
        
        # Parse the response
        fields_json = response.choices[0].message.content.strip()
        # Clean up the response if it has markdown code blocks
        if "```json" in fields_json:
            fields_json = fields_json.split("```json")[1].split("```")[0].strip()
        elif "```" in fields_json:
            fields_json = fields_json.split("```")[1].split("```")[0].strip()
        
        fields_data = json.loads(fields_json)
        
        # Convert to FieldInfo objects
        fields = []
        for field_dict in fields_data:
            fields.append(FieldInfo(
                name=field_dict.get("name", "field"),
                type=field_dict.get("type", "string"),
                description=field_dict.get("description", ""),
                required=field_dict.get("required", False)
            ))
        
        # Always add a full_content field as the first option
        fields.insert(0, FieldInfo(
            name="full_content",
            type="string",
            description="Complete document content",
            required=False
        ))
        
        logger.info(f"AI generated {len(fields)} dynamic fields for document")
        return fields[:15]  # Limit to 15 fields
    
    def _extract_fields_fallback(self, markdown: str) -> List[FieldInfo]:
        """
        Fallback method using pattern-based field detection.
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
        
        # Look for common patterns
        patterns_found = []
        
        # Check for dates
        if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]* \d{1,2},? \d{4}', markdown_lower):
            patterns_found.append(FieldInfo(name="dates", type="string", description="Dates found in document", required=False))
        
        # Check for money/amounts
        if re.search(r'\$[\d,]+\.?\d*|usd|eur|gbp|\d+\.\d{2}', markdown_lower):
            patterns_found.append(FieldInfo(name="amounts", type="string", description="Monetary amounts", required=False))
        
        # Check for email addresses
        if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', markdown):
            patterns_found.append(FieldInfo(name="email_addresses", type="string", description="Email addresses", required=False))
        
        # Check for phone numbers
        if re.search(r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}', markdown):
            patterns_found.append(FieldInfo(name="phone_numbers", type="string", description="Phone numbers", required=False))
        
        # Check for specific document types
        if any(word in markdown_lower for word in ['invoice', 'bill', 'receipt']):
            patterns_found.extend([
                FieldInfo(name="invoice_number", type="string", description="Invoice/Bill number", required=False),
                FieldInfo(name="total_amount", type="string", description="Total amount", required=False),
                FieldInfo(name="vendor_name", type="string", description="Vendor/Company name", required=False),
            ])
        
        if any(word in markdown_lower for word in ['contract', 'agreement']):
            patterns_found.extend([
                FieldInfo(name="parties", type="string", description="Parties involved", required=False),
                FieldInfo(name="effective_date", type="string", description="Effective date", required=False),
            ])
        
        # Add pattern-based fields
        fields.extend(patterns_found)
        
        # Generic fields to ensure we have options
        if len(fields) < 5:
            fields.extend([
                FieldInfo(name="key_information", type="string", description="Key information", required=False),
                FieldInfo(name="summary", type="string", description="Document summary", required=False),
            ])
        
        # Remove duplicates
        seen = set()
        unique_fields = []
        for field in fields:
            if field.name not in seen:
                seen.add(field.name)
                unique_fields.append(field)
        
        return unique_fields[:15]
    
    def _extract_fields_using_openai(self, markdown: str, selected_fields: List[str]) -> Dict[str, Any]:
        """
        Use OpenAI to extract specific fields from the markdown content.
        Handles both single and multiple value extraction.
        """
        if not OpenAI or not settings.OPENAI_API_KEY:
            logger.warning("OpenAI not available for field extraction")
            return {field: None for field in selected_fields}
        
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Determine which fields should return arrays
            multi_value_keywords = ['id', 'number', 'code', 'reference', 'date', 'email', 'phone', 
                                   'address', 'name', 'amount', 'item', 'line', 'entry', 'record']
            
            # Prepare field descriptions for the prompt
            fields_desc = []
            for field in selected_fields:
                field_lower = field.lower()
                is_multi = any(keyword in field_lower for keyword in multi_value_keywords)
                
                # Special handling for apex_id
                if field == 'apex_id':
                    fields_desc.append(f"- apex_id: Extract the Apex ID which appears as 'Apex ID: ' followed by an alphanumeric code like '25USOA26564'. Look for text that says 'Apex ID:', 'APEX ID:', or similar variations. Return ALL apex IDs found as an array.")
                elif is_multi:
                    fields_desc.append(f"- {field}: Extract ALL {field.replace('_', ' ')} values as an array. If multiple occurrences exist across pages, include all of them")
                else:
                    fields_desc.append(f"- {field}: Extract the {field.replace('_', ' ')} as a single value")
            
            fields_desc_str = "\n".join(fields_desc)
            
            prompt = f"""Extract the following specific fields from this document. 
            Return a JSON object with the exact field names as keys.
            For fields that should be arrays, return ALL occurrences found throughout the document.
            If a field cannot be found, set its value to null (or empty array [] for array fields).
            
            Fields to extract:
            {fields_desc_str}
            
            Document content:
            {markdown[:6000]}  # Increased to capture more content
            
            Return ONLY a valid JSON object with the requested fields. Example:
            {{
                "apex_id": ["ID001", "ID002", "ID003"],  // array for multiple values
                "title": "Document Title",  // single value
                "dates": ["2024-01-01", "2024-02-01"]  // array for multiple dates
            }}
            """
            
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL or "gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a data extraction expert. Extract specific fields from documents and return them as JSON. When a field appears multiple times in the document, return ALL occurrences as an array. Pay special attention to identifiers like 'Apex ID:' which may appear with various formats and capitalizations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for accurate extraction
                max_tokens=2000  # Increased for larger arrays
            )
            
            # Parse the response
            extracted_json = response.choices[0].message.content.strip()
            # Clean up the response if it has markdown code blocks
            if "```json" in extracted_json:
                extracted_json = extracted_json.split("```json")[1].split("```")[0].strip()
            elif "```" in extracted_json:
                extracted_json = extracted_json.split("```")[1].split("```")[0].strip()
            
            extracted_data = json.loads(extracted_json)
            
            # Ensure all requested fields are present
            for field in selected_fields:
                if field not in extracted_data:
                    field_lower = field.lower()
                    is_multi = any(keyword in field_lower for keyword in multi_value_keywords)
                    extracted_data[field] = [] if is_multi else None
            
            logger.info(f"OpenAI extracted fields: {list(extracted_data.keys())}")
            return extracted_data
            
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {str(e)}")
            return {field: None for field in selected_fields}
    
    def _create_json_schema_from_fields(self, selected_fields: List[str], custom_field_descriptions: Dict[str, str] = {}) -> Dict:
        """
        Create a JSON Schema from selected fields for Landing.AI API.
        Fields that typically have multiple values (IDs, numbers, dates, emails) are defined as arrays.
        """
        properties = {}
        for field in selected_fields:
            # Get description from custom fields or generate one
            description = custom_field_descriptions.get(field, f"Extract all {field.replace('_', ' ')} values from the document")
            
            # Determine if this field should support multiple values
            # Fields containing these keywords typically appear multiple times in documents
            multi_value_keywords = ['id', 'number', 'code', 'reference', 'date', 'email', 'phone', 
                                   'address', 'name', 'amount', 'item', 'line', 'entry', 'record']
            
            field_lower = field.lower()
            should_be_array = any(keyword in field_lower for keyword in multi_value_keywords)
            
            if should_be_array:
                # Define as array to capture all occurrences
                properties[field] = {
                    "type": "array",
                    "items": {"type": "string"},
                    "title": field.replace('_', ' ').title(),
                    "description": description + " (all occurrences)",
                    "uniqueItems": True  # Avoid duplicate values
                }
            else:
                # Single value field
                properties[field] = {
                    "type": "string",
                    "title": field.replace('_', ' ').title(),
                    "description": description
                }
        
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": "Document Extraction Schema",
            "description": "Schema for extracting selected fields from document",
            "type": "object",
            "properties": properties,
            "required": []  # Make all fields optional
        }
        
        return schema
    
    async def extract_with_structured_model(self, file_path: str, extraction_model: Optional[BaseModel] = None, max_pages: int = 45) -> Optional[ExtractionResult]:
        """
        Use Landing.AI SDK with ParseConfig for structured extraction.
        Respects the 45-page limit for structured extraction.
        
        Args:
            file_path: Path to the document
            extraction_model: Pydantic model for structured extraction
            max_pages: Maximum pages to process (default 50 for Landing.AI limit)
            
        Returns:
            ExtractionResult with extracted data
        """
        if not parse or not ParseConfig:
            logger.error("Landing.AI SDK not available")
            return None
            
        try:
            # Create ParseConfig with extraction model
            config = ParseConfig(
                api_key=self.api_key,
                extraction_model=extraction_model,
                include_marginalia=True,
                include_metadata_in_markdown=True,
                extraction_split_size=max_pages  # Respect the 45-page limit
            )
            
            logger.info(f"Processing {file_path} with structured extraction model")
            logger.info(f"Max pages per batch: {max_pages}")
            
            # Parse with the configured settings
            result = parse(file_path, config=config)
            
            if result:
                # Extract the structured data
                extracted_data = {}
                if hasattr(result, 'extraction') and result.extraction:
                    if isinstance(result.extraction, list):
                        # Multiple extractions (one per page/form)
                        extracted_data = {
                            "forms": [item.dict() if hasattr(item, 'dict') else item for item in result.extraction],
                            "total_forms": len(result.extraction)
                        }
                    else:
                        # Single extraction
                        extracted_data = result.extraction.dict() if hasattr(result.extraction, 'dict') else result.extraction
                
                return ExtractionResult(
                    data=extracted_data,
                    markdown=result.markdown if hasattr(result, 'markdown') else "",
                    processed_at=datetime.utcnow(),
                    extraction_metadata={
                        "method": "structured_model",
                        "model_name": extraction_model.__name__ if extraction_model else "None",
                        "max_pages": max_pages
                    }
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Structured extraction failed: {str(e)}")
            if "exceeds the maximum of 50 pages" in str(e) or "exceeds the maximum of 45 pages" in str(e):
                logger.error("Document exceeds 45-page limit for structured extraction. Consider splitting the document first.")
            return None
    
    async def _extract_using_landing_ai_api(self, file_path: str, selected_fields: List[str], custom_field_descriptions: Dict[str, str] = {}) -> Optional[Dict[str, Any]]:
        """
        Use Landing.AI's agentic-document-analysis API endpoint for extraction.
        """
        if not self.api_key:
            logger.warning("No Landing.AI API key available")
            return None
        
        try:
            # Create JSON schema from fields
            schema = self._create_json_schema_from_fields(selected_fields, custom_field_descriptions)
            logger.info(f"Created JSON schema for Landing.AI: {json.dumps(schema, indent=2)}")
            
            # Prepare the request
            headers = {"Authorization": f"Basic {self.api_key}"}
            
            # Open the file and prepare for upload
            with open(file_path, 'rb') as pdf_file:
                files = [
                    ("pdf", (os.path.basename(file_path), pdf_file, "application/pdf"))
                ]
                payload = {"fields_schema": json.dumps(schema)}
                
                # Make the API request
                response = requests.post(
                    self.api_endpoint,
                    headers=headers,
                    files=files,
                    data=payload,
                    timeout=60  # 60 second timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "data" in result and "extracted_schema" in result["data"]:
                        extracted_data = result["data"]["extracted_schema"]
                        logger.info(f"Landing.AI API extracted: {list(extracted_data.keys())}")
                        return extracted_data
                    else:
                        logger.warning(f"Unexpected response structure from Landing.AI: {result}")
                        return None
                else:
                    logger.error(f"Landing.AI API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Landing.AI API extraction failed: {str(e)}")
            return None
    
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
        selected_fields: List[str],
        custom_fields: Optional[List[dict]] = None
    ) -> ExtractionResult:
        """
        Extract data from document using provided schema.
        First tries Landing.AI extraction, then falls back to OpenAI extraction.
        """
        logger.info(f"Extracting from document: {file_path}")
        logger.info(f"Selected fields: {selected_fields}")
        logger.info(f"Custom fields: {custom_fields}")
        
        if parse is None:
            # Mock response with chunk telemetry for development
            mock_data = {field: f"Sample {field} value" for field in selected_fields}
            if custom_fields:
                for field in custom_fields:
                    mock_data[field['name']] = f"Sample {field['name']} value"
            
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
            # Create dynamic schema from selected_fields and custom_fields
            from pydantic import create_model, Field
            from typing import Optional
            
            # Build field definitions
            field_definitions = {}
            
            # Add selected fields (from OptInFormExtraction model)
            for field_name in selected_fields:
                # Create more descriptive field descriptions for better extraction
                field_desc = f"Extract the {field_name.replace('_', ' ')} from the document. Look for text, labels, or sections that indicate '{field_name.replace('_', ' ')}' or similar variations."
                field_definitions[field_name] = (Optional[str], Field(default=None, description=field_desc))
            
            # Add custom fields
            if custom_fields:
                for field in custom_fields:
                    field_name = field.get('name')
                    field_type = field.get('type', 'str')
                    
                    # Create specific descriptions for known fields to improve extraction accuracy
                    if field_name == 'apex_id':
                        field_desc = "The Apex ID identifier found in the document, typically appearing as 'Apex ID: ' followed by an alphanumeric code starting with '25USOA' and followed by numbers (e.g., 'Apex ID: 25USOA26564'). Look for text that explicitly says 'Apex ID:' or 'APEX ID:' in the document header or body."
                    elif field_name == 'case_number':
                        field_desc = "The case number or filing number, typically a numeric or alphanumeric identifier used to reference the case in legal or administrative proceedings."
                    elif field_name == 'filing_date':
                        field_desc = "The date when the document was filed or submitted, typically in MM/DD/YYYY or similar date format."
                    elif field_name == 'court_name':
                        field_desc = "The name of the court or tribunal where the case is being heard."
                    elif field_name == 'plaintiff':
                        field_desc = "The name of the plaintiff or petitioner in the legal proceeding."
                    elif field_name == 'defendant':
                        field_desc = "The name of the defendant or respondent in the legal proceeding."
                    else:
                        # Use user-provided description or create a more detailed default
                        user_desc = field.get('description', '')
                        if user_desc:
                            field_desc = user_desc
                        else:
                            field_desc = f"Extract the {field_name.replace('_', ' ')} value from the document. Look for labels, headers, or text that indicates '{field_name.replace('_', ' ')}' or similar variations."
                    
                    # Map type string to Python type
                    python_type = str  # default
                    if field_type == 'bool':
                        python_type = bool
                    elif field_type == 'int':
                        python_type = int
                    elif field_type == 'float':
                        python_type = float
                    
                    field_definitions[field_name] = (Optional[python_type], Field(default=None, description=field_desc))
            
            # Log field definitions for debugging
            logger.info(f"Creating dynamic model with {len(field_definitions)} fields:")
            for field_name, (field_type, field_obj) in field_definitions.items():
                logger.info(f"  - {field_name}: {field_obj.description}")
            
            # Create dynamic model
            DynamicExtractionModel = create_model('DynamicExtractionModel', **field_definitions)
            
            # First try using Landing.AI SDK/Library
            logger.info("Attempting extraction with Landing.AI SDK/Library (preferred for paid plan)")
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: parse(
                    documents=[file_path],
                    extraction_model=DynamicExtractionModel
                )
            )
            
            if not result or len(result) == 0:
                # If extraction with schema fails, try to get markdown without schema
                logger.info("Extraction with schema failed, trying to get markdown only")
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
                    # Prepare all fields for extraction
                    all_fields = list(selected_fields)
                    if custom_fields:
                        all_fields.extend([f['name'] for f in custom_fields])
                    
                    # Use OpenAI to extract fields from markdown
                    if markdown_content and OpenAI and settings.OPENAI_API_KEY:
                        logger.info("Using OpenAI to extract fields from markdown")
                        extracted_data = self._extract_fields_using_openai(markdown_content, all_fields)
                        extraction_method = "OPENAI_FALLBACK"
                    else:
                        extracted_data = {field: None for field in all_fields}
                        extraction_method = "FAILED"
                    
                    return ExtractionResult(
                        data=extracted_data,
                        markdown=markdown_content,
                        processed_at=datetime.now(),
                        metadata={"extraction_method": extraction_method}
                    )
                
                raise Exception("No results from parse")
            
            parsed_doc = result[0]
            
            # Always try to get markdown first
            markdown_content = getattr(parsed_doc, 'markdown', '')
            
            # Get extracted data if available from Landing.AI
            extracted_data = {}
            if hasattr(parsed_doc, 'extraction') and parsed_doc.extraction:
                extracted_data = parsed_doc.extraction.model_dump()
                logger.info(f"Landing.AI extracted data keys: {list(extracted_data.keys())}")
                logger.info(f"Landing.AI extracted data values: {extracted_data}")
                # Check specifically for apex_id
                if 'apex_id' in extracted_data:
                    logger.info(f"apex_id value from Landing.AI: {extracted_data.get('apex_id')}")
            
            # Check if Landing.AI extraction was successful for the selected fields
            # If not, use OpenAI to extract the specific fields
            needs_openai_extraction = False
            if not extracted_data:
                logger.info("No extraction data from Landing.AI, will use OpenAI")
                needs_openai_extraction = True
            else:
                # Check if we got meaningful data (not just full_content)
                non_null_fields = [k for k, v in extracted_data.items() if v is not None and k != 'full_content']
                if len(non_null_fields) == 0:
                    logger.info("Landing.AI only returned full_content, will use OpenAI for specific fields")
                    needs_openai_extraction = True
            
            # Track which extraction method was ultimately used
            extraction_method = "LANDING_AI_SDK"  # Default if Landing.AI SDK worked
            
            if needs_openai_extraction and markdown_content:
                logger.info("Using OpenAI to extract specific fields from markdown")
                all_fields_for_extraction = list(selected_fields)
                if custom_fields:
                    all_fields_for_extraction.extend([f['name'] for f in custom_fields])
                extracted_data = self._extract_fields_using_openai(markdown_content, all_fields_for_extraction)
                extraction_method = "OPENAI_FALLBACK"
            
            # Filter to only include requested fields (both selected and custom)
            all_requested_fields = list(selected_fields)
            if custom_fields:
                all_requested_fields.extend([f['name'] for f in custom_fields])
            
            filtered_data = {
                field: extracted_data.get(field, None) 
                for field in all_requested_fields
            }
            
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
            
            # Log which extraction method was used
            logger.info(f"Extraction completed using method: {extraction_method}")
            
            return ExtractionResult(
                data=result_data,
                markdown=markdown_content,
                processed_at=datetime.now(),
                metadata={"extraction_method": extraction_method}
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