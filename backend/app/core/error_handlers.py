from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import logging
from typing import Union

logger = logging.getLogger(__name__)

class ExtractionError(Exception):
    """Custom exception for extraction-specific errors"""
    def __init__(self, message: str, error_code: str = "EXTRACTION_ERROR", status_code: int = 400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)

class SchemaValidationError(ExtractionError):
    """Error for schema validation failures"""
    def __init__(self, message: str):
        super().__init__(message, "SCHEMA_VALIDATION_ERROR", 422)

class LandingAIError(ExtractionError):
    """Error for Landing AI SDK failures"""
    def __init__(self, message: str):
        super().__init__(message, "LANDING_AI_ERROR", 503)

class DocumentNotFoundError(ExtractionError):
    """Error when document is not found"""
    def __init__(self, document_id: int):
        super().__init__(f"Document with ID {document_id} not found", "DOCUMENT_NOT_FOUND", 404)

async def extraction_error_handler(request: Request, exc: ExtractionError):
    """Handle extraction-specific errors"""
    logger.error(f"Extraction error: {exc.message} (Code: {exc.error_code})")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "code": exc.error_code,
                "type": type(exc).__name__
            },
            "retry_allowed": exc.error_code not in ["DOCUMENT_NOT_FOUND", "SCHEMA_VALIDATION_ERROR"],
            "escalation_available": True
        }
    )

async def database_error_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    logger.error(f"Database error: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "message": "A database error occurred. Please try again later.",
                "code": "DATABASE_ERROR",
                "type": "SQLAlchemyError"
            },
            "retry_allowed": True,
            "escalation_available": True
        }
    )

async def general_error_handler(request: Request, exc: Exception):
    """Handle general errors"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "message": "An unexpected error occurred. Please try again later.",
                "code": "INTERNAL_ERROR",
                "type": "Exception"
            },
            "retry_allowed": True,
            "escalation_available": True
        }
    )

def sanitize_error_message(message: str) -> str:
    """Remove sensitive information from error messages"""
    # Remove file paths
    import re
    message = re.sub(r'/[\w/\-\.]+', '[PATH]', message)
    # Remove potential API keys or tokens
    message = re.sub(r'[a-zA-Z0-9]{32,}', '[REDACTED]', message)
    # Remove email addresses
    message = re.sub(r'[\w\.-]+@[\w\.-]+', '[EMAIL]', message)
    
    return message