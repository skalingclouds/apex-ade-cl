from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class FieldInfo(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    required: bool = True

class ParseResponse(BaseModel):
    fields: List[FieldInfo]
    document_type: Optional[str] = None
    confidence: Optional[float] = None
    markdown: Optional[str] = None

class FieldSelection(BaseModel):
    selected_fields: List[str]

class ExtractionRequest(BaseModel):
    selected_fields: List[str]
    custom_fields: Optional[List[FieldInfo]] = []

class ExtractionResponse(BaseModel):
    success: bool
    extracted_data: Optional[Dict[str, Any]] = None
    markdown: Optional[str] = None
    error: Optional[str] = None

# Saved schema DTOs
class SavedSchemaCreate(BaseModel):
    name: str
    description: Optional[str] = None
    fields: List[FieldInfo]

class SavedSchemaResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    fields: List[FieldInfo]
    is_active: bool
    created_at: Any
    updated_at: Any

class BatchProcessRequest(BaseModel):
    document_ids: List[int]
    schema_id: Optional[int] = None
    selected_fields: Optional[List[str]] = None
    custom_fields: Optional[List[FieldInfo]] = None
    concurrency: Optional[int] = 4