from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
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

    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int