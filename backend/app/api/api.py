from fastapi import APIRouter

from app.api.endpoints import documents, chat, extraction, export, analytics, document_management

api_router = APIRouter()

# Include document_management router BEFORE documents router to avoid route conflicts
# The /by-status and /stats routes must come before /{document_id} catch-all route
api_router.include_router(document_management.router, prefix="/documents", tags=["management"])
api_router.include_router(chat.router, prefix="/documents", tags=["chat"])
api_router.include_router(extraction.router, prefix="/documents", tags=["extraction"])
api_router.include_router(export.router, prefix="/documents", tags=["export"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])