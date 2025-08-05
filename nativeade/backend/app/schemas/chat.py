from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime

class ChatRequest(BaseModel):
    query: str

class HighlightArea(BaseModel):
    page: int
    x: float
    y: float
    width: float
    height: float

class ChatResponse(BaseModel):
    id: int
    query: str
    response: str
    highlighted_areas: Optional[List[HighlightArea]] = None
    created_at: datetime

    class Config:
        from_attributes = True