from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class AnalyticsMetrics(BaseModel):
    """Overall analytics metrics"""
    total_documents: int
    status_distribution: Dict[str, int]
    approval_rate: float
    rejection_rate: float
    total_chat_interactions: int
    unique_documents_chatted: int
    average_chats_per_document: float
    total_exports: int
    recent_uploads_24h: int
    recent_chats_24h: int

class TimeSeriesData(BaseModel):
    """Time series data point"""
    date: str
    value: int

class StatusDistribution(BaseModel):
    """Document status distribution"""
    status: str
    count: int
    percentage: float

class PerformanceMetrics(BaseModel):
    """System performance metrics"""
    average_chat_response_time_ms: float
    document_failure_rate: float
    chat_fallback_rate: float
    total_failed_documents: int
    total_fallback_chats: int

class EventSummary(BaseModel):
    """Analytics event summary"""
    event_type: str
    count: int
    last_occurrence: Optional[datetime]