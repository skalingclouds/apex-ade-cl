from typing import Optional, Any
from sqlalchemy.orm import Session
from fastapi import Request
import json
from datetime import datetime

from app.models.audit_log import AuditLog
from app.models.document import Document, DocumentStatus

class AuditService:
    def __init__(self, db: Session, request: Optional[Request] = None):
        self.db = db
        self.request = request
    
    def log_status_change(
        self, 
        document_id: int, 
        old_status: DocumentStatus, 
        new_status: DocumentStatus,
        reason: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Log a document status change"""
        audit_log = AuditLog(
            document_id=document_id,
            action="status_change",
            old_value=old_status.value if old_status else None,
            new_value=new_status.value,
            user_id=user_id,
            ip_address=self._get_client_ip() if self.request else None,
            user_agent=self._get_user_agent() if self.request else None,
            details=json.dumps({"reason": reason}) if reason else None
        )
        self.db.add(audit_log)
        self.db.commit()
        return audit_log
    
    def log_extraction(
        self, 
        document_id: int, 
        selected_fields: list,
        success: bool,
        error_message: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Log an extraction attempt"""
        details = {
            "selected_fields": selected_fields,
            "success": success,
            "error_message": error_message
        }
        
        audit_log = AuditLog(
            document_id=document_id,
            action="extraction",
            old_value=None,
            new_value="success" if success else "failed",
            user_id=user_id,
            ip_address=self._get_client_ip() if self.request else None,
            user_agent=self._get_user_agent() if self.request else None,
            details=json.dumps(details)
        )
        self.db.add(audit_log)
        self.db.commit()
        return audit_log
    
    def log_document_access(
        self, 
        document_id: int, 
        action: str,
        user_id: Optional[str] = None
    ):
        """Log document access (view, download, etc.)"""
        audit_log = AuditLog(
            document_id=document_id,
            action=f"document_{action}",
            user_id=user_id,
            ip_address=self._get_client_ip() if self.request else None,
            user_agent=self._get_user_agent() if self.request else None
        )
        self.db.add(audit_log)
        self.db.commit()
        return audit_log
    
    def log_deletion(
        self, 
        document_id: int, 
        document_data: dict,
        user_id: Optional[str] = None
    ):
        """Log document deletion for GDPR compliance"""
        # Store anonymized document info before deletion
        anonymized_data = {
            "filename": document_data.get("filename", ""),
            "upload_date": document_data.get("uploaded_at", ""),
            "deletion_reason": "user_requested"
        }
        
        audit_log = AuditLog(
            document_id=document_id,
            action="deletion",
            old_value=json.dumps(anonymized_data),
            new_value="deleted",
            user_id=user_id,
            ip_address=self._get_client_ip() if self.request else None,
            user_agent=self._get_user_agent() if self.request else None,
            details=json.dumps({"gdpr_compliant": True})
        )
        self.db.add(audit_log)
        self.db.commit()
        return audit_log
    
    def log_document_action(
        self, 
        document_id: int, 
        action: str,
        metadata: Optional[dict] = None,
        user_id: Optional[str] = None
    ):
        """Log a generic document action"""
        audit_log = AuditLog(
            document_id=document_id,
            action=action,
            user_id=user_id,
            ip_address=self._get_client_ip() if self.request else None,
            user_agent=self._get_user_agent() if self.request else None,
            details=json.dumps(metadata) if metadata else None
        )
        self.db.add(audit_log)
        self.db.commit()
        return audit_log
    
    def log_bulk_action(
        self, 
        action: str,
        metadata: dict,
        user_id: Optional[str] = None
    ):
        """Log a bulk action affecting multiple documents"""
        audit_log = AuditLog(
            document_id=None,  # No single document ID for bulk actions
            action=action,
            user_id=user_id,
            ip_address=self._get_client_ip() if self.request else None,
            user_agent=self._get_user_agent() if self.request else None,
            details=json.dumps(metadata)
        )
        self.db.add(audit_log)
        self.db.commit()
        return audit_log
    
    def log_bulk_access(
        self, 
        action: str,
        metadata: dict,
        user_id: Optional[str] = None
    ):
        """Log bulk access operations"""
        audit_log = AuditLog(
            document_id=None,
            action=action,
            user_id=user_id,
            ip_address=self._get_client_ip() if self.request else None,
            user_agent=self._get_user_agent() if self.request else None,
            details=json.dumps(metadata)
        )
        self.db.add(audit_log)
        self.db.commit()
        return audit_log
    
    def _get_client_ip(self) -> Optional[str]:
        """Extract client IP from request"""
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
        """Extract user agent from request"""
        if not self.request:
            return None
        
        return self.request.headers.get("User-Agent")