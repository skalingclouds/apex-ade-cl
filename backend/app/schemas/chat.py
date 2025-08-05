from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime

class ChatRequest(BaseModel):
    query: str

class HighlightArea(BaseModel):
    page: int
    bbox: List[float]  # [x1, y1, x2, y2] bounding box coordinates

class ChatResponse(BaseModel):
    id: int
    query: str
    response: str
    highlighted_areas: Optional[List[HighlightArea]] = None
    fallback: Optional[bool] = False
    created_at: datetime

    class Config:
        from_attributes = True