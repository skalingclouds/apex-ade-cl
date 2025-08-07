#!/usr/bin/env python3
"""
Start the Apex ADE backend server with configuration for large file uploads
"""
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    # Configure uvicorn to handle large file uploads (900MB+)
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        # Set max request body size to match our configuration (1GB)
        limit_max_requests=1000,
        # Important: increase the request body size limit
        # Default is 100MB, we need 1GB for large PDFs
        h11_max_incomplete_event_size=settings.MAX_UPLOAD_SIZE,
        # Increase timeout for large file uploads
        timeout_keep_alive=300,  # 5 minutes
        # Log level
        log_level="info"
    )