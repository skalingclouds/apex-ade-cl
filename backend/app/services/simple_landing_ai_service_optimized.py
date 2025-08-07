"""
Optimized Landing.AI service for paid plan users
Prioritizes SDK/Library for unlimited page parsing, with proper fallback order
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
    from agentic_doc.utils import viz_parsed_document
except ImportError:
    parse = None
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

class OptimizedLandingAIService:
    """
    Optimized for paid plan users:
    - SDK/Library: Unlimited pages for parsing, 50 for extraction
    - API: 50 pages max, 25 requests/minute
    - Prioritizes SDK over API for better page limits
    """
    
    def __init__(self):
        self.api_key = settings.VISION_AGENT_API_KEY
        self.api_endpoint = "https://api.va.landing.ai/v1/tools/agentic-document-analysis"
        
        # Ensure the environment variable is set for the SDK
        if self.api_key:
            os.environ['VISION_AGENT_API_KEY'] = self.api_key
            logger.info(f"OptimizedLandingAIService initialized with API key (Paid Plan)")
        else:
            logger.warning("No VISION_AGENT_API_KEY found in settings")
    
    async def extract_document_optimized(
        self, 
        file_path: str,
        schema_model: type[BaseModel],
        selected_fields: List[str],
        custom_descriptions: Optional[Dict[str, str]] = None
    ) -> ExtractionResult:
        """
        Optimized extraction order for paid plan:
        1. SDK/Library (unlimited pages for parsing, best for large docs)
        2. API (fallback if SDK fails, limited to 50 pages)
        3. OpenAI (last resort for consistency)
        """
        logger.info(f"Starting optimized extraction for: {file_path}")
        logger.info(f"Selected fields: {selected_fields}")
        
        if not custom_descriptions:
            custom_descriptions = {}
            for field_name, field_info in schema_model.__fields__.items():
                if hasattr(field_info, 'description') and field_info.description:
                    custom_descriptions[field_name] = field_info.description
        
        # Phase 1: Try SDK/Library first (best for large documents)
        logger.info("Phase 1: Attempting Landing.AI SDK extraction (unlimited pages for parsing)")
        sdk_result = await self._try_sdk_extraction(file_path, schema_model, selected_fields)
        if sdk_result:
            return sdk_result
        
        # Phase 2: Try API if SDK fails
        logger.info("Phase 2: SDK failed, trying Landing.AI API (limited to 50 pages)")
        api_result = await self._try_api_extraction(file_path, selected_fields, custom_descriptions)
        if api_result:
            return api_result
        
        # Phase 3: OpenAI fallback (last resort)
        logger.info("Phase 3: Landing.AI methods failed, using OpenAI fallback")
        openai_result = await self._try_openai_extraction(file_path, selected_fields)
        if openai_result:
            return openai_result
        
        # All methods failed
        logger.error("All extraction methods failed")
        return ExtractionResult(
            data={field: None for field in selected_fields},
            markdown="",
            processed_at=datetime.now(),
            metadata={"extraction_method": "FAILED"}
        )
    
    async def _try_sdk_extraction(
        self,
        file_path: str,
        schema_model: type[BaseModel],
        selected_fields: List[str]
    ) -> Optional[ExtractionResult]:
        """Try extraction using Landing.AI SDK"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: parse(
                    documents=[file_path],
                    extraction_model=schema_model,
                    include_marginalia=True,
                    include_metadata_in_markdown=True
                )
            )
            
            if result and len(result) > 0:
                parsed_doc = result[0]
                markdown_content = getattr(parsed_doc, 'markdown', '')
                
                # Check if we got extracted data
                extracted_data = {}
                if hasattr(parsed_doc, 'extraction') and parsed_doc.extraction:
                    extracted_data = parsed_doc.extraction.model_dump()
                    
                    # Verify we got meaningful data
                    non_null_fields = [k for k, v in extracted_data.items() 
                                     if v is not None and k != 'full_content']
                    
                    if non_null_fields:
                        logger.info(f"SDK extraction successful with fields: {non_null_fields}")
                        
                        # Filter to requested fields
                        filtered_data = {
                            field: extracted_data.get(field, None) 
                            for field in selected_fields
                        }
                        
                        return ExtractionResult(
                            data=filtered_data,
                            markdown=markdown_content,
                            processed_at=datetime.now(),
                            metadata={"extraction_method": "LANDING_AI_SDK"}
                        )
                
                logger.info("SDK parsing successful but extraction incomplete")
            
        except Exception as e:
            logger.error(f"SDK extraction failed: {str(e)}")
        
        return None
    
    async def _try_api_extraction(
        self,
        file_path: str,
        selected_fields: List[str],
        custom_descriptions: Dict[str, str]
    ) -> Optional[ExtractionResult]:
        """Try extraction using Landing.AI API"""
        if not self.api_key:
            logger.warning("No API key for Landing.AI API")
            return None
        
        try:
            # Create JSON schema for API
            schema = self._create_json_schema_from_fields(selected_fields, custom_descriptions)
            
            headers = {"Authorization": f"Basic {self.api_key}"}
            
            with open(file_path, 'rb') as pdf_file:
                files = [("pdf", (os.path.basename(file_path), pdf_file, "application/pdf"))]
                payload = {"fields_schema": json.dumps(schema)}
                
                response = requests.post(
                    self.api_endpoint,
                    headers=headers,
                    files=files,
                    data=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "data" in result and "extracted_schema" in result["data"]:
                        extracted_data = result["data"]["extracted_schema"]
                        logger.info(f"API extraction successful: {list(extracted_data.keys())}")
                        
                        # Get markdown separately
                        loop = asyncio.get_event_loop()
                        parse_result = await loop.run_in_executor(
                            None,
                            lambda: parse(
                                documents=[file_path],
                                include_marginalia=True,
                                include_metadata_in_markdown=True
                            )
                        )
                        
                        markdown_content = ""
                        if parse_result and len(parse_result) > 0:
                            markdown_content = getattr(parse_result[0], 'markdown', '')
                        
                        return ExtractionResult(
                            data=extracted_data,
                            markdown=markdown_content,
                            processed_at=datetime.now(),
                            metadata={"extraction_method": "LANDING_AI_API"}
                        )
                else:
                    logger.error(f"API error: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"API extraction failed: {str(e)}")
        
        return None
    
    async def _try_openai_extraction(
        self,
        file_path: str,
        selected_fields: List[str]
    ) -> Optional[ExtractionResult]:
        """Try extraction using OpenAI (last resort)"""
        if not OpenAI or not settings.OPENAI_API_KEY:
            logger.warning("OpenAI not available for fallback")
            return None
        
        try:
            # First get markdown using SDK parsing (unlimited pages)
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
                markdown_content = getattr(result[0], 'markdown', '')
                
                if markdown_content:
                    # Use OpenAI to extract fields
                    logger.warning("Using OpenAI fallback - consistency may vary")
                    extracted_data = self._extract_fields_using_openai(markdown_content, selected_fields)
                    
                    return ExtractionResult(
                        data=extracted_data,
                        markdown=markdown_content,
                        processed_at=datetime.now(),
                        metadata={"extraction_method": "OPENAI_FALLBACK"}
                    )
                    
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {str(e)}")
        
        return None
    
    def _create_json_schema_from_fields(
        self, 
        selected_fields: List[str], 
        custom_descriptions: Dict[str, str] = {}
    ) -> dict:
        """Create JSON Schema 2020-12 for Landing.AI API"""
        # Keywords that suggest multi-value fields
        multi_value_keywords = ['id', 'number', 'date', 'name', 'code', 'reference']
        
        properties = {}
        for field in selected_fields:
            description = custom_descriptions.get(field, f"Extract {field} from document")
            
            # Check if this should be a multi-value field
            is_multi_value = any(keyword in field.lower() for keyword in multi_value_keywords)
            
            if is_multi_value:
                properties[field] = {
                    "type": "array",
                    "items": {"type": "string"},
                    "title": field.replace('_', ' ').title(),
                    "description": description + " (all occurrences)",
                    "uniqueItems": True
                }
            else:
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
            "required": []  # All fields optional
        }
        
        return schema
    
    def _extract_fields_using_openai(self, markdown: str, selected_fields: List[str]) -> Dict[str, Any]:
        """Extract fields using OpenAI"""
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Truncate markdown if too long
        markdown_sample = markdown[:5000] if len(markdown) > 5000 else markdown
        
        # Keywords for multi-value detection
        multi_value_keywords = ['id', 'number', 'date', 'name', 'code', 'reference']
        
        # Build field specifications
        field_specs = []
        for field in selected_fields:
            is_multi_value = any(keyword in field.lower() for keyword in multi_value_keywords)
            if is_multi_value:
                field_specs.append(f"- {field}: Extract ALL occurrences as an array")
            else:
                field_specs.append(f"- {field}: Extract single value")
        
        prompt = f"""Extract these specific fields from the document. Return ONLY a JSON object.
        
Fields to extract:
{chr(10).join(field_specs)}

Document content:
{markdown_sample}

Return a JSON object with the requested fields. Use arrays for multi-value fields, single values otherwise.
For fields not found, use null. Example:
{{"apex_id": ["ID1", "ID2"], "date": "2024-01-01", "amount": null}}
"""
        
        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL or "gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            # Clean up response
            content = re.sub(r'^```json\s*', '', content)
            content = re.sub(r'\s*```$', '', content)
            
            extracted_data = json.loads(content)
            
            # Ensure all requested fields are present
            for field in selected_fields:
                if field not in extracted_data:
                    is_multi_value = any(keyword in field.lower() for keyword in multi_value_keywords)
                    extracted_data[field] = [] if is_multi_value else None
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"OpenAI extraction error: {str(e)}")
            # Return empty structure
            result = {}
            for field in selected_fields:
                is_multi_value = any(keyword in field.lower() for keyword in multi_value_keywords)
                result[field] = [] if is_multi_value else None
            return result