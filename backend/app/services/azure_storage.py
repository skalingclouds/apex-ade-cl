import os
import uuid
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Union
from urllib.parse import urlparse

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions

from app.core.config import settings


def _get_blob_service_client() -> BlobServiceClient:
    """Create a blob service client using the storage account credentials."""
    connection_string = (
        f"DefaultEndpointsProtocol=https;"
        f"AccountName={settings.AZURE_STORAGE_ACCOUNT_NAME};"
        f"AccountKey={settings.AZURE_STORAGE_ACCOUNT_KEY};"
        f"EndpointSuffix=core.windows.net"
    )
    return BlobServiceClient.from_connection_string(connection_string)


def generate_sas_for_blob(
    filename: str, 
    content_type: Optional[str] = None, 
    size: Optional[int] = None
) -> Dict[str, str]:
    """
    Generate a SAS token for uploading a blob to Azure Storage.
    
    Args:
        filename: The original filename
        content_type: The MIME type of the content (optional)
        size: The size of the file in bytes (optional)
        
    Returns:
        Dict with keys:
            - upload_url: The URL with SAS token for uploading
            - blob_url: The base URL for the blob (without SAS token)
            - expires_at: ISO format timestamp when the SAS token expires
    """
    # Validate Azure storage settings
    if not all([
        settings.AZURE_STORAGE_ACCOUNT_NAME,
        settings.AZURE_STORAGE_ACCOUNT_KEY,
        settings.AZURE_STORAGE_CONTAINER_NAME
    ]):
        raise ValueError("Azure Storage settings are not properly configured")
    
    # Create a unique blob name with timestamp to avoid collisions
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    # Keep the original file extension if present
    _, ext = os.path.splitext(filename)
    
    # Sanitize filename - replace spaces and special chars
    safe_filename = os.path.basename(filename).replace(" ", "_")
    safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c in '._-')
    
    # Construct blob name with timestamp prefix
    blob_name = f"{timestamp}_{unique_id}_{safe_filename}"
    
    # Calculate expiry time
    start_time = datetime.utcnow()
    expiry_time = start_time + timedelta(minutes=settings.AZURE_SAS_TTL_MINUTES)
    
    # Set SAS permissions (create, write, read)
    sas_permissions = BlobSasPermissions(read=True, create=True, write=True)
    
    # Generate the SAS token
    sas_token = generate_blob_sas(
        account_name=settings.AZURE_STORAGE_ACCOUNT_NAME,
        container_name=settings.AZURE_STORAGE_CONTAINER_NAME,
        blob_name=blob_name,
        account_key=settings.AZURE_STORAGE_ACCOUNT_KEY,
        permission=sas_permissions,
        expiry=expiry_time,
        start=start_time
    )
    
    # Construct the base URL and signed URL
    base_url = (
        f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/"
        f"{settings.AZURE_STORAGE_CONTAINER_NAME}/{blob_name}"
    )
    
    signed_url = f"{base_url}?{sas_token}"
    
    return {
        "upload_url": signed_url,
        "blob_url": base_url,
        "expires_at": expiry_time.isoformat()
    }


def download_blob_to_path(blob_url: str, dest_path: str) -> int:
    """
    Download a blob from Azure Storage to a local file path.
    
    Args:
        blob_url: The URL of the blob to download
        dest_path: The local file path to save the blob
        
    Returns:
        int: The number of bytes written to the file
        
    Raises:
        ValueError: If the blob URL is invalid
        requests.HTTPError: If the download fails
    """
    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
    
    # Parse the blob URL to extract container and blob name
    parsed_url = urlparse(blob_url)
    if not parsed_url.netloc or not parsed_url.path:
        raise ValueError(f"Invalid blob URL format: {blob_url}")
    
    # Stream the download with 8MB chunks
    chunk_size = 8 * 1024 * 1024  # 8MB
    total_bytes = 0
    
    # Use requests to stream the download
    with requests.get(blob_url, stream=True) as response:
        response.raise_for_status()  # Raise exception for HTTP errors
        
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # Filter out keep-alive chunks
                    f.write(chunk)
                    total_bytes += len(chunk)
    
    return total_bytes


def extract_blob_info_from_url(blob_url: str) -> Dict[str, str]:
    """
    Extract account, container, and blob name from a blob URL.
    
    Args:
        blob_url: The URL of the blob
        
    Returns:
        Dict with keys:
            - account_name: The storage account name
            - container_name: The container name
            - blob_name: The blob name
    """
    parsed_url = urlparse(blob_url)
    
    # Extract account name from netloc (e.g., "accountname.blob.core.windows.net")
    netloc_parts = parsed_url.netloc.split('.')
    if len(netloc_parts) < 4 or netloc_parts[1] != 'blob':
        raise ValueError(f"Invalid blob URL format: {blob_url}")
    
    account_name = netloc_parts[0]
    
    # Extract container and blob name from path (e.g., "/container/path/to/blob")
    path_parts = parsed_url.path.strip('/').split('/', 1)
    if len(path_parts) < 2:
        raise ValueError(f"Invalid blob URL path format: {blob_url}")
    
    container_name = path_parts[0]
    blob_name = path_parts[1]
    
    return {
        "account_name": account_name,
        "container_name": container_name,
        "blob_name": blob_name
    }
