from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator
import json
from app.models.document import DocumentStatus

class DocumentBase(BaseModel):
    filename: str

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    status: Optional[DocumentStatus] = None
    extracted_md: Optional[str] = None
    extracted_data: Optional[dict] = None
    error_message: Optional[str] = None
    processed_at: Optional[datetime] = None

class DocumentResponse(DocumentBase):
    id: int
    filepath: str
    status: DocumentStatus
    extracted_md: Optional[str] = None
    extracted_data: Optional[dict] = None
    error_message: Optional[str] = None
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    updated_at: datetime
    archived: bool = False
    archived_at: Optional[datetime] = None
    archived_by: Optional[str] = None

    @field_validator('extracted_data', mode='before')
    @classmethod
    def parse_extracted_data(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v

    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    page: int = 1
    pages: int = 1

class RejectRequest(BaseModel):
    reason: Optional[str] = None

class EscalateRequest(BaseModel):
    reason: Optional[str] = None