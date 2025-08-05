from fastapi import APIRouter

from app.api.endpoints import documents, chat, extraction, export

api_router = APIRouter()

api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/documents", tags=["chat"])
api_router.include_router(extraction.router, prefix="/documents", tags=["extraction"])
api_router.include_router(export.router, prefix="/documents", tags=["export"])