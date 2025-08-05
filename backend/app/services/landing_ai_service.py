from typing import List, Dict, Any, Type
from datetime import datetime
from pathlib import Path
import asyncio
from pydantic import BaseModel

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

class ExtractionResult(BaseModel):
    data: Dict[str, Any]
    markdown: str
    processed_at: datetime

class LandingAIService:
    def __init__(self):
        self.api_key = settings.LANDING_AI_API_KEY
    
    async def parse_document(self, file_path: str) -> ParseResponse:
        """Parse document to identify extractable fields"""
        
        # For MVP, we'll use the agentic_doc parse function
        if parse is None:
            # Mock response for development
            return ParseResponse(
                fields=[
                    FieldInfo(name="product_name", type="string", description="Product name"),
                    FieldInfo(name="brand", type="string", description="Brand name"),
                    FieldInfo(name="price", type="number", description="Product price"),
                    FieldInfo(name="description", type="string", description="Product description"),
                ],
                document_type="product_catalog",
                confidence=0.95
            )
        
        # Run parse in executor to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            parse,
            [file_path],
            None,  # result_save_dir
            None,  # grounding_save_dir
            True,  # include_marginalia
            True   # include_metadata_in_markdown
        )
        
        # Extract fields from the parsed document
        if result and len(result) > 0:
            parsed_doc = result[0]
            
            # Analyze chunks to determine available fields
            fields = self._analyze_chunks_for_fields(parsed_doc.chunks)
            
            return ParseResponse(
                fields=fields,
                document_type=parsed_doc.doc_type,
                confidence=0.9  # You might calculate this based on parse quality
            )
        
        raise Exception("Failed to parse document")
    
    async def extract_document(
        self, 
        file_path: str,
        schema_model: Type[BaseModel],
        selected_fields: List[str]
    ) -> ExtractionResult:
        """Extract data from document using provided schema"""
        
        if parse is None:
            # Mock response for development
            mock_data = {
                field: f"Sample {field}" for field in selected_fields
            }
            return ExtractionResult(
                data=mock_data,
                markdown=f"# Extracted Data\n\n" + "\n".join([f"**{k}**: {v}" for k, v in mock_data.items()]),
                processed_at=datetime.now()
            )
        
        # Run extraction with the dynamic schema
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            parse,
            [file_path],
            None,  # result_save_dir
            None,  # grounding_save_dir
            True,  # include_marginalia
            True,  # include_metadata_in_markdown
            schema_model  # extraction_model
        )
        
        if result and len(result) > 0:
            parsed_doc = result[0]
            
            # Extract the data according to schema
            if hasattr(parsed_doc, 'extraction') and parsed_doc.extraction:
                extracted_data = parsed_doc.extraction.model_dump()
                
                # Filter to only selected fields
                filtered_data = {
                    field: extracted_data.get(field, None) 
                    for field in selected_fields
                }
                
                # Validate extracted data against schema
                try:
                    validated_data = schema_model(**filtered_data)
                    validated_dict = validated_data.model_dump()
                except Exception as validation_error:
                    # If validation fails, still return the data but log the error
                    import logging
                    logging.warning(f"Validation error: {validation_error}")
                    validated_dict = filtered_data
                
                return ExtractionResult(
                    data=validated_dict,
                    markdown=parsed_doc.markdown,
                    processed_at=datetime.now()
                )
        
        raise Exception("Failed to extract document data - no extraction results found")
    
    def _analyze_chunks_for_fields(self, chunks: List[Any]) -> List[FieldInfo]:
        """Analyze document chunks to determine available fields"""
        fields = []
        seen_fields = set()
        
        # Analyze chunk types and content
        chunk_types = set()
        has_forms = False
        has_numbers = False
        
        for chunk in chunks:
            if hasattr(chunk, 'chunk_type') and chunk.chunk_type:
                chunk_types.add(chunk.chunk_type.value)
            
            # Check for form-like content
            if hasattr(chunk, 'text'):
                text = chunk.text.lower()
                if any(keyword in text for keyword in ['name:', 'date:', 'address:', 'phone:', 'email:']):
                    has_forms = True
                if any(char.isdigit() for char in text):
                    has_numbers = True
        
        # Document structure fields
        if 'title' in chunk_types or any(hasattr(c, 'text') and len(c.text) < 100 for c in chunks[:3]):
            fields.append(FieldInfo(name="title", type="string", description="Document title"))
            seen_fields.add("title")
        
        # Table data fields
        if 'table' in chunk_types:
            fields.extend([
                FieldInfo(name="table_data", type="array", description="Extracted table data"),
                FieldInfo(name="table_headers", type="array", description="Table column headers", required=False),
            ])
            seen_fields.update(["table_data", "table_headers"])
        
        # Text content fields
        if 'text' in chunk_types or 'paragraph' in chunk_types:
            fields.extend([
                FieldInfo(name="content", type="string", description="Main document content"),
                FieldInfo(name="summary", type="string", description="Document summary", required=False),
            ])
            seen_fields.update(["content", "summary"])
        
        # Form fields
        if has_forms:
            form_fields = [
                FieldInfo(name="name", type="string", description="Name field", required=False),
                FieldInfo(name="date", type="date", description="Date field", required=False),
                FieldInfo(name="address", type="string", description="Address field", required=False),
                FieldInfo(name="phone", type="string", description="Phone number", required=False),
                FieldInfo(name="email", type="string", description="Email address", required=False),
            ]
            for field in form_fields:
                if field.name not in seen_fields:
                    fields.append(field)
                    seen_fields.add(field.name)
        
        # Numeric fields
        if has_numbers:
            numeric_fields = [
                FieldInfo(name="amount", type="number", description="Monetary amount", required=False),
                FieldInfo(name="quantity", type="integer", description="Quantity or count", required=False),
                FieldInfo(name="total", type="number", description="Total value", required=False),
            ]
            for field in numeric_fields:
                if field.name not in seen_fields:
                    fields.append(field)
                    seen_fields.add(field.name)
        
        # Common metadata fields
        metadata_fields = [
            FieldInfo(name="author", type="string", description="Document author", required=False),
            FieldInfo(name="created_date", type="date", description="Creation date", required=False),
            FieldInfo(name="page_count", type="integer", description="Number of pages", required=False),
            FieldInfo(name="language", type="string", description="Document language", required=False),
            FieldInfo(name="category", type="string", description="Document category", required=False),
            FieldInfo(name="metadata", type="object", description="Additional metadata", required=False),
        ]
        
        for field in metadata_fields:
            if field.name not in seen_fields:
                fields.append(field)
                seen_fields.add(field.name)
        
        return fields