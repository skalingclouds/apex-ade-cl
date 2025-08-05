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

class FieldSelection(BaseModel):
    selected_fields: List[str]

class ExtractionRequest(BaseModel):
    selected_fields: List[str]

class ExtractionResponse(BaseModel):
    success: bool
    extracted_data: Optional[Dict[str, Any]] = None
    markdown: Optional[str] = None
    error: Optional[str] = None