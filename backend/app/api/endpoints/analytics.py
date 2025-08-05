from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from datetime import datetime, timedelta
from typing import Dict, Any, List

from app.core.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.analytics_event import AnalyticsEvent, EventType
from app.models.chat_log import ChatLog
from app.schemas.analytics import AnalyticsMetrics, TimeSeriesData, StatusDistribution

router = APIRouter()

@router.get("/metrics", response_model=AnalyticsMetrics)
def get_analytics_metrics(
    db: Session = Depends(get_db)
):
    """Get overall analytics metrics (admin endpoint)"""
    # TODO: Add admin authentication/authorization
    
    # Total documents processed
    total_documents = db.query(func.count(Document.id)).scalar()
    
    # Documents by status
    status_counts = db.query(
        Document.status,
        func.count(Document.id)
    ).group_by(Document.status).all()
    
    status_distribution = {
        status.value: count for status, count in status_counts
    }
    
    # Calculate approval/rejection rates
    approved_count = status_distribution.get(DocumentStatus.APPROVED.value, 0)
    rejected_count = status_distribution.get(DocumentStatus.REJECTED.value, 0)
    extracted_count = status_distribution.get(DocumentStatus.EXTRACTED.value, 0)
    
    total_reviewed = approved_count + rejected_count + extracted_count
    approval_rate = (approved_count / total_reviewed * 100) if total_reviewed > 0 else 0
    rejection_rate = (rejected_count / total_reviewed * 100) if total_reviewed > 0 else 0
    
    # Chat interaction metrics
    total_chats = db.query(func.count(ChatLog.id)).scalar()
    unique_docs_chatted = db.query(func.count(func.distinct(ChatLog.document_id))).scalar()
    
    # Average chats per document (for documents that have chats)
    avg_chats_per_doc = (total_chats / unique_docs_chatted) if unique_docs_chatted > 0 else 0
    
    # Export metrics from analytics events
    export_count = db.query(func.count(AnalyticsEvent.id)).filter(
        AnalyticsEvent.event_type == EventType.DOCUMENT_EXPORTED
    ).scalar()
    
    # Recent activity (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_uploads = db.query(func.count(Document.id)).filter(
        Document.uploaded_at >= yesterday
    ).scalar()
    
    recent_chats = db.query(func.count(ChatLog.id)).filter(
        ChatLog.created_at >= yesterday
    ).scalar()
    
    return AnalyticsMetrics(
        total_documents=total_documents,
        status_distribution=status_distribution,
        approval_rate=round(approval_rate, 2),
        rejection_rate=round(rejection_rate, 2),
        total_chat_interactions=total_chats,
        unique_documents_chatted=unique_docs_chatted,
        average_chats_per_document=round(avg_chats_per_doc, 2),
        total_exports=export_count,
        recent_uploads_24h=recent_uploads,
        recent_chats_24h=recent_chats
    )

@router.get("/metrics/timeseries", response_model=List[TimeSeriesData])
def get_timeseries_metrics(
    metric: str = "uploads",
    days: int = 7,
    db: Session = Depends(get_db)
):
    """Get time series data for a specific metric (admin endpoint)"""
    # TODO: Add admin authentication/authorization
    
    if days > 30:
        days = 30  # Limit to 30 days
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    if metric == "uploads":
        # Get daily upload counts
        query = db.query(
            func.date(Document.uploaded_at).label('date'),
            func.count(Document.id).label('count')
        ).filter(
            Document.uploaded_at >= start_date
        ).group_by(func.date(Document.uploaded_at))
    
    elif metric == "chats":
        # Get daily chat counts
        query = db.query(
            func.date(ChatLog.created_at).label('date'),
            func.count(ChatLog.id).label('count')
        ).filter(
            ChatLog.created_at >= start_date
        ).group_by(func.date(ChatLog.created_at))
    
    elif metric == "approvals":
        # Get daily approval counts from analytics events
        query = db.query(
            func.date(AnalyticsEvent.created_at).label('date'),
            func.count(AnalyticsEvent.id).label('count')
        ).filter(
            and_(
                AnalyticsEvent.event_type == EventType.DOCUMENT_APPROVED,
                AnalyticsEvent.created_at >= start_date
            )
        ).group_by(func.date(AnalyticsEvent.created_at))
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid metric: {metric}. Valid options: uploads, chats, approvals"
        )
    
    results = query.all()
    
    # Convert to response format
    timeseries = [
        TimeSeriesData(
            date=result.date.isoformat() if hasattr(result.date, 'isoformat') else str(result.date),
            value=result.count
        )
        for result in results
    ]
    
    return timeseries

@router.get("/metrics/top-users", response_model=List[Dict[str, Any]])
def get_top_users(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get top users by activity (admin endpoint)"""
    # TODO: Add admin authentication/authorization
    
    # Since we don't have user authentication yet, we'll use IP addresses as a proxy
    top_uploaders = db.query(
        AnalyticsEvent.ip_address,
        func.count(AnalyticsEvent.id).label('upload_count')
    ).filter(
        and_(
            AnalyticsEvent.event_type == EventType.DOCUMENT_UPLOAD,
            AnalyticsEvent.ip_address.isnot(None)
        )
    ).group_by(
        AnalyticsEvent.ip_address
    ).order_by(
        func.count(AnalyticsEvent.id).desc()
    ).limit(limit).all()
    
    return [
        {
            "user_identifier": result.ip_address or "Anonymous",
            "upload_count": result.upload_count
        }
        for result in top_uploaders
    ]

@router.get("/metrics/performance", response_model=Dict[str, Any])
def get_performance_metrics(
    db: Session = Depends(get_db)
):
    """Get system performance metrics (admin endpoint)"""
    # TODO: Add admin authentication/authorization
    
    # Average chat response time
    avg_chat_time = db.query(
        func.avg(AnalyticsEvent.duration_ms)
    ).filter(
        and_(
            AnalyticsEvent.event_type == EventType.CHAT_INTERACTION,
            AnalyticsEvent.duration_ms.isnot(None)
        )
    ).scalar()
    
    # Failed document percentage
    failed_count = db.query(func.count(Document.id)).filter(
        Document.status == DocumentStatus.FAILED
    ).scalar()
    total_processed = db.query(func.count(Document.id)).filter(
        Document.status != DocumentStatus.PENDING
    ).scalar()
    
    failure_rate = (failed_count / total_processed * 100) if total_processed > 0 else 0
    
    # Chat fallback rate
    fallback_chats = db.query(func.count(ChatLog.id)).filter(
        ChatLog.fallback == True
    ).scalar()
    total_chats = db.query(func.count(ChatLog.id)).scalar()
    
    fallback_rate = (fallback_chats / total_chats * 100) if total_chats > 0 else 0
    
    return {
        "average_chat_response_time_ms": round(avg_chat_time, 2) if avg_chat_time else 0,
        "document_failure_rate": round(failure_rate, 2),
        "chat_fallback_rate": round(fallback_rate, 2),
        "total_failed_documents": failed_count,
        "total_fallback_chats": fallback_chats
    }

@router.get("/events/recent", response_model=List[Dict[str, Any]])
def get_recent_events(
    limit: int = 50,
    event_type: str = None,
    db: Session = Depends(get_db)
):
    """Get recent analytics events (admin endpoint)"""
    # TODO: Add admin authentication/authorization
    
    query = db.query(AnalyticsEvent)
    
    if event_type:
        query = query.filter(AnalyticsEvent.event_type == event_type)
    
    events = query.order_by(AnalyticsEvent.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": event.id,
            "event_type": event.event_type,
            "document_id": event.document_id,
            "created_at": event.created_at.isoformat(),
            "event_data": event.event_data,
            "duration_ms": event.duration_ms,
            "ip_address": event.ip_address
        }
        for event in events
    ]