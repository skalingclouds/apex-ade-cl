from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from fastapi import Request, BackgroundTasks
import logging
import json
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.models.analytics_event import AnalyticsEvent, EventType

logger = logging.getLogger(__name__)

# Thread pool for non-blocking database operations
executor = ThreadPoolExecutor(max_workers=2)

class AnalyticsService:
    def __init__(self, db: Session, request: Optional[Request] = None, background_tasks: Optional[BackgroundTasks] = None):
        self.db = db
        self.request = request
        self.background_tasks = background_tasks
    
    def log_event(
        self,
        event_type: EventType,
        document_id: Optional[int] = None,
        user_id: Optional[str] = None,
        event_data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None
    ):
        """Log an analytics event. If background_tasks is available, log asynchronously."""
        if self.background_tasks:
            # Log asynchronously in background
            self.background_tasks.add_task(
                self._log_event_sync,
                event_type,
                document_id,
                user_id,
                event_data,
                duration_ms
            )
        else:
            # Log synchronously but with error handling
            try:
                self._log_event_sync(
                    event_type,
                    document_id,
                    user_id,
                    event_data,
                    duration_ms
                )
            except Exception as e:
                logger.error(f"Failed to log analytics event: {str(e)}")
    
    def _log_event_sync(
        self,
        event_type: EventType,
        document_id: Optional[int] = None,
        user_id: Optional[str] = None,
        event_data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None
    ):
        """Synchronous event logging with error handling."""
        try:
            event = AnalyticsEvent(
                event_type=event_type,
                document_id=document_id,
                user_id=user_id,
                session_id=self._get_session_id() if self.request else None,
                event_data=event_data,
                duration_ms=duration_ms,
                ip_address=self._get_client_ip() if self.request else None,
                user_agent=self._get_user_agent() if self.request else None,
                client_version=self._get_client_version() if self.request else None
            )
            
            self.db.add(event)
            self.db.commit()
            logger.debug(f"Analytics event logged: {event_type}")
        except SQLAlchemyError as e:
            logger.error(f"Database error logging analytics event: {str(e)}")
            self.db.rollback()
        except Exception as e:
            logger.error(f"Unexpected error logging analytics event: {str(e)}")
    
    def log_document_upload(self, document_id: int, filename: str, file_size: int):
        """Log document upload event."""
        self.log_event(
            EventType.DOCUMENT_UPLOAD,
            document_id=document_id,
            event_data={
                "filename": filename,
                "file_size": file_size
            }
        )
    
    def log_document_status_change(self, document_id: int, old_status: str, new_status: str, reason: Optional[str] = None):
        """Log document status change events."""
        event_type_map = {
            "parsed": EventType.DOCUMENT_PARSED,
            "extracted": EventType.DOCUMENT_EXTRACTED,
            "approved": EventType.DOCUMENT_APPROVED,
            "rejected": EventType.DOCUMENT_REJECTED,
            "escalated": EventType.DOCUMENT_ESCALATED
        }
        
        event_type = event_type_map.get(new_status.lower())
        if event_type:
            self.log_event(
                event_type,
                document_id=document_id,
                event_data={
                    "old_status": old_status,
                    "new_status": new_status,
                    "reason": reason
                }
            )
    
    def log_chat_interaction(self, document_id: int, query: str, response_length: int, 
                           highlighted_areas: int, fallback: bool, duration_ms: Optional[float] = None):
        """Log chat interaction event."""
        self.log_event(
            EventType.CHAT_INTERACTION,
            document_id=document_id,
            event_data={
                "query_length": len(query),
                "response_length": response_length,
                "highlighted_areas": highlighted_areas,
                "fallback": fallback
            },
            duration_ms=duration_ms
        )
    
    def log_document_export(self, document_id: int, export_format: str, file_size: Optional[int] = None):
        """Log document export event."""
        self.log_event(
            EventType.DOCUMENT_EXPORTED,
            document_id=document_id,
            event_data={
                "format": export_format,
                "file_size": file_size
            }
        )
    
    def log_extraction_retry(self, document_id: int, attempt: int, error_message: Optional[str] = None):
        """Log extraction retry event."""
        self.log_event(
            EventType.EXTRACTION_RETRY,
            document_id=document_id,
            event_data={
                "attempt": attempt,
                "error_message": error_message
            }
        )
    
    def _get_client_ip(self) -> Optional[str]:
        """Extract client IP from request."""
        if not self.request:
            return None
        
        # Check for forwarded IP first
        forwarded = self.request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Fall back to direct connection
        if self.request.client:
            return self.request.client.host
        
        return None
    
    def _get_user_agent(self) -> Optional[str]:
        """Extract user agent from request."""
        if not self.request:
            return None
        
        return self.request.headers.get("User-Agent")
    
    def _get_session_id(self) -> Optional[str]:
        """Extract session ID from request."""
        if not self.request:
            return None
        
        # Try to get from cookie or header
        session_id = self.request.cookies.get("session_id")
        if not session_id:
            session_id = self.request.headers.get("X-Session-ID")
        
        return session_id
    
    def _get_client_version(self) -> Optional[str]:
        """Extract client version from request."""
        if not self.request:
            return None
        
        return self.request.headers.get("X-Client-Version")

# Analytics query methods for reporting
class AnalyticsQuery:
    def __init__(self, db: Session):
        self.db = db
    
    def get_event_counts_by_type(self, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """Get event counts by type for a date range."""
        try:
            results = self.db.query(
                AnalyticsEvent.event_type,
                func.count(AnalyticsEvent.id).label('count')
            ).filter(
                AnalyticsEvent.created_at >= start_date,
                AnalyticsEvent.created_at <= end_date
            ).group_by(AnalyticsEvent.event_type).all()
            
            return {result.event_type: result.count for result in results}
        except Exception as e:
            logger.error(f"Error querying event counts: {str(e)}")
            return {}
    
    def get_document_activity(self, document_id: int) -> list:
        """Get all analytics events for a specific document."""
        try:
            events = self.db.query(AnalyticsEvent).filter(
                AnalyticsEvent.document_id == document_id
            ).order_by(AnalyticsEvent.created_at.desc()).all()
            
            return events
        except Exception as e:
            logger.error(f"Error querying document activity: {str(e)}")
            return []
    
    def get_user_activity(self, user_id: str, limit: int = 100) -> list:
        """Get recent activity for a specific user."""
        try:
            events = self.db.query(AnalyticsEvent).filter(
                AnalyticsEvent.user_id == user_id
            ).order_by(AnalyticsEvent.created_at.desc()).limit(limit).all()
            
            return events
        except Exception as e:
            logger.error(f"Error querying user activity: {str(e)}")
            return []