from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
import os
import threading
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.models.document import Document, DocumentStatus
from app.schemas.document import DocumentResponse
from app.services.azure_storage import generate_sas_for_blob, download_blob_to_path
from app.api.endpoints.documents import process_large_document_async

# Pydantic models for request/response
from pydantic import BaseModel, Field


class SasUrlRequest(BaseModel):
    filename: str
    content_type: Optional[str] = Field(default="application/pdf")
    size: Optional[int] = None


class SasUrlResponse(BaseModel):
    uploadUrl: str
    blobUrl: str
    expiresAt: str


class BlobRegisterRequest(BaseModel):
    blob_url: str
    filename: str
    size: Optional[int] = None


router = APIRouter()


@router.post("/azure-sas", response_model=SasUrlResponse)
async def get_azure_sas_url(
    request: SasUrlRequest,
):
    """
    Generate a SAS URL for direct upload to Azure Blob Storage.
    """
    if settings.STORAGE_MODE != "azure":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Azure Blob Storage is not enabled in this environment",
        )

    try:
        sas_info = generate_sas_for_blob(
            filename=request.filename,
            content_type=request.content_type,
            size=request.size,
        )
        
        return SasUrlResponse(
            uploadUrl=sas_info["upload_url"],
            blobUrl=sas_info["blob_url"],
            expiresAt=sas_info["expires_at"],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SAS URL: {str(e)}",
        )


def download_and_process_blob(document_id: int, blob_url: str, local_path: str):
    """
    Background task to download a blob and process it if needed.
    This runs in a separate thread.
    """
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Download the blob to local storage
        print(f"Starting download of blob {blob_url} to {local_path}")
        file_size_bytes = download_blob_to_path(blob_url, local_path)
        file_size_mb = file_size_bytes / (1024 * 1024)
        
        # Update document with file size
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.file_size_mb = file_size_mb
            
            # If large file, trigger chunking
            if file_size_mb > 40:
                document.is_chunked = True
                document.status = DocumentStatus.CHUNKING
                db.commit()
                
                # Create an async event loop to run the chunking process
                import asyncio
                
                def run_async_chunking():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(
                            process_large_document_async(document_id, local_path)
                        )
                    finally:
                        loop.close()
                
                # Start chunking in a daemon thread
                chunking_thread = threading.Thread(
                    target=run_async_chunking, daemon=True
                )
                chunking_thread.start()
                print(f"Started chunking process for document {document_id}")
            else:
                # Small file, mark as ready for processing
                document.status = DocumentStatus.PENDING
                db.commit()
                print(f"Document {document_id} ready for processing")
    except Exception as e:
        # Update document status to failed
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = DocumentStatus.FAILED
            document.error_message = f"Azure download failed: {str(e)}"
            db.commit()
        print(f"Error downloading blob for document {document_id}: {str(e)}")
    finally:
        db.close()


@router.post("/register", response_model=DocumentResponse)
async def register_blob(
    request: BlobRegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Register an uploaded blob as a document and start background download.
    """
    if settings.STORAGE_MODE != "azure":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Azure Blob Storage is not enabled in this environment",
        )

    try:
        # Create a unique filename for local storage
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        local_filename = f"{timestamp}_{request.filename}"
        local_filepath = os.path.join(settings.UPLOAD_DIRECTORY, local_filename)
        
        # Create document record with PENDING status initially
        document = Document(
            filename=request.filename,
            filepath=local_filepath,
            status=DocumentStatus.PENDING,  # Will be updated by background task
            file_size_mb=request.size / (1024 * 1024) if request.size else None,
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Start background download task
        background_tasks.add_task(
            download_and_process_blob,
            document_id=document.id,
            blob_url=request.blob_url,
            local_path=local_filepath,
        )
        
        return document
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register blob: {str(e)}",
        )
