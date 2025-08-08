"""
PDF Chunking Service for processing large documents
Handles splitting PDFs into manageable chunks for consistent extraction
"""
import os
import asyncio
import logging
from typing import List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk, ChunkStatus, ProcessingLog, ProcessingMetrics
from app.core.config import settings

logger = logging.getLogger(__name__)

class PDFChunker:
    """
    Intelligent PDF chunking service that splits large documents
    into smaller, processable chunks while maintaining consistency
    
    Optimized for Landing.AI Paid Plan:
    - API/Library extraction limit: 50 pages per request
    - Default chunk size: 40 pages (safe margin under 50-page limit)
    - Rate limit: 25 requests/minute
    """
    
    def __init__(self, 
                 max_pages_per_chunk: int = 40,  # Increased for paid plan (50 page limit)
                 max_chunk_size_mb: float = 15.0,  # Increased for larger chunks
                 chunk_overlap: int = 0):
        """
        Initialize PDF Chunker
        
        Args:
            max_pages_per_chunk: Maximum pages in a single chunk (default 40 for paid plan)
            max_chunk_size_mb: Maximum file size for a chunk in MB
            chunk_overlap: Number of pages to overlap between chunks (for context)
        """
        self.max_pages_per_chunk = max_pages_per_chunk
        self.max_chunk_size_mb = max_chunk_size_mb
        self.chunk_overlap = chunk_overlap
        self.upload_dir = Path(settings.UPLOAD_DIRECTORY)
        self.chunks_dir = self.upload_dir / "chunks"
        self.chunks_dir.mkdir(exist_ok=True)
    
    async def should_chunk_document(self, file_path: str) -> Tuple[bool, int, float]:
        """
        Determine if a document needs chunking based on size and page count
        
        Returns:
            Tuple of (should_chunk, page_count, file_size_mb)
        """
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            # Get page count
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                page_count = len(pdf_reader.pages)
            
            # Chunk if file is large OR has many pages
            should_chunk = (
                file_size_mb > 50 or  # Files over 50MB
                page_count > 100  # Documents over 100 pages
            )
            
            logger.info(f"Document analysis: {page_count} pages, {file_size_mb:.2f}MB, chunking={'Yes' if should_chunk else 'No'}")
            
            return should_chunk, page_count, file_size_mb
            
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            return False, 0, 0
    
    async def create_chunks(self, 
                          document: Document, 
                          db: Session,
                          chunk_size: int = None) -> List[DocumentChunk]:
        """
        Create chunks for a document and save them to database
        
        Args:
            document: Document model instance
            db: Database session
            chunk_size: Optional custom chunk size (overrides default)
            
        Returns:
            List of created DocumentChunk instances
        """
        try:
            # Check if chunking is needed
            should_chunk, page_count, file_size_mb = await self.should_chunk_document(document.filepath)
            
            # Update document with metadata
            document.page_count = page_count
            document.file_size_mb = file_size_mb
            
            if not should_chunk:
                # Document doesn't need chunking
                document.is_chunked = False
                db.commit()
                logger.info(f"Document {document.id} doesn't require chunking")
                return []
            
            # Update document status
            document.status = DocumentStatus.CHUNKING
            document.is_chunked = True
            db.commit()
            
            # Use custom chunk size if provided, otherwise use default
            effective_chunk_size = chunk_size if chunk_size else self.max_pages_per_chunk
            
            # Log the start of chunking
            log_entry = ProcessingLog(
                document_id=document.id,
                action="CHUNKING_START",
                level="INFO",
                message=f"Starting to chunk document: {page_count} pages, {file_size_mb:.2f}MB",
                metadata={
                    "page_count": page_count,
                    "file_size_mb": file_size_mb,
                    "chunk_size": effective_chunk_size
                }
            )
            db.add(log_entry)
            
            # Create chunks
            chunks = await self._split_pdf_into_chunks(
                document.filepath,
                document.id,
                page_count,
                chunk_size=effective_chunk_size
            )
            
            # Save chunks to database
            db_chunks = []
            for chunk_info in chunks:
                chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_number=chunk_info['chunk_number'],
                    start_page=chunk_info['start_page'],
                    end_page=chunk_info['end_page'],
                    page_count=chunk_info['page_count'],
                    file_path=chunk_info['file_path'],
                    file_size_mb=chunk_info['file_size_mb'],
                    status=ChunkStatus.PENDING,
                    retry_count=0,
                    max_retries=3
                )
                db.add(chunk)
                db_chunks.append(chunk)
            
            # Update document with chunk information
            document.total_chunks = len(chunks)
            document.completed_chunks = 0
            document.chunk_size = effective_chunk_size
            
            # Create processing metrics
            metrics = ProcessingMetrics(
                document_id=document.id,
                total_pages=page_count,
                total_chunks=len(chunks),
                processed_pages=0,
                completed_chunks=0,
                failed_chunks=0,
                landing_ai_api_count=0,
                landing_ai_sdk_count=0,
                openai_fallback_count=0,
                is_complete=False,
                has_failures=False
            )
            db.add(metrics)
            
            # Log successful chunking
            log_entry = ProcessingLog(
                document_id=document.id,
                action="CHUNKING_COMPLETE",
                level="INFO",
                message=f"Successfully created {len(chunks)} chunks",
                metadata={
                    "total_chunks": len(chunks),
                    "chunks": [{"number": c['chunk_number'], 
                              "pages": f"{c['start_page']}-{c['end_page']}"} 
                              for c in chunks]
                }
            )
            db.add(log_entry)
            
            db.commit()
            logger.info(f"Created {len(chunks)} chunks for document {document.id}")
            
            return db_chunks
            
        except Exception as e:
            logger.error(f"Error creating chunks for document {document.id}: {str(e)}")
            
            # Log the error
            log_entry = ProcessingLog(
                document_id=document.id,
                action="CHUNKING_FAILED",
                level="ERROR",
                message=f"Failed to create chunks: {str(e)}",
                metadata={"error": str(e)}
            )
            db.add(log_entry)
            
            document.status = DocumentStatus.FAILED
            document.error_message = f"Chunking failed: {str(e)}"
            db.commit()
            
            raise
    
    async def _split_pdf_into_chunks(self, 
                                    pdf_path: str, 
                                    document_id: int,
                                    total_pages: int,
                                    chunk_size: int = None) -> List[dict]:
        """
        Split PDF into physical chunk files
        
        Returns:
            List of chunk information dictionaries
        """
        chunks = []
        chunk_number = 1
        
        try:
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                
                # Use custom chunk size if provided
                effective_chunk_size = chunk_size if chunk_size else self.max_pages_per_chunk
                
                # Calculate chunks
                for start_page in range(0, total_pages, effective_chunk_size - self.chunk_overlap):
                    end_page = min(start_page + effective_chunk_size, total_pages)
                    
                    # Create chunk filename
                    chunk_filename = f"doc_{document_id}_chunk_{chunk_number:03d}.pdf"
                    chunk_path = self.chunks_dir / chunk_filename
                    
                    # Create PDF writer for this chunk
                    pdf_writer = PdfWriter()
                    
                    # Add pages to chunk
                    for page_num in range(start_page, end_page):
                        pdf_writer.add_page(pdf_reader.pages[page_num])
                    
                    # Write chunk to file
                    with open(chunk_path, 'wb') as chunk_file:
                        pdf_writer.write(chunk_file)
                    
                    # Get chunk file size
                    chunk_size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
                    
                    # Add chunk info
                    chunks.append({
                        'chunk_number': chunk_number,
                        'start_page': start_page + 1,  # Convert to 1-based indexing
                        'end_page': end_page,
                        'page_count': end_page - start_page,
                        'file_path': str(chunk_path),
                        'file_size_mb': chunk_size_mb
                    })
                    
                    logger.info(f"Created chunk {chunk_number}: pages {start_page+1}-{end_page}, {chunk_size_mb:.2f}MB")
                    chunk_number += 1
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting PDF: {str(e)}")
            raise
    
    def calculate_optimal_chunk_size(self, 
                                    document: Document,
                                    current_performance: Optional[dict] = None) -> int:
        """
        Dynamically calculate optimal chunk size based on document characteristics
        and system performance
        
        Optimized for Landing.AI Paid Plan:
        - Hard limit: 50 pages (API/Library extraction limit)
        - Sweet spot: 30-40 pages for most documents
        - Adjust down for heavy pages or slow API response
        
        Args:
            document: Document being processed
            current_performance: Current processing metrics (API response times, etc.)
            
        Returns:
            Optimal number of pages per chunk
        """
        base_size = self.max_pages_per_chunk  # Default 40 for paid plan
        
        # Adjust based on file size
        if document.file_size_mb and document.page_count:
            avg_page_size_mb = document.file_size_mb / document.page_count
            
            if avg_page_size_mb > 0.5:  # Heavy pages (lots of images/content)
                base_size = min(base_size, 25)  # Reduce for heavy pages
            elif avg_page_size_mb > 1.0:  # Very heavy pages
                base_size = min(base_size, 15)  # Further reduction
        
        # Adjust based on current performance
        if current_performance:
            avg_response_time = current_performance.get('avg_api_response_ms', 0)
            if avg_response_time > 15000:  # API is slow (>15 seconds)
                base_size = min(base_size, 25)
            elif avg_response_time > 30000:  # API is very slow (>30 seconds)
                base_size = min(base_size, 15)
        
        # Paid plan limits: minimum 10 pages (efficient), maximum 45 (safety margin)
        return max(10, min(base_size, 45))
    
    async def cleanup_chunks(self, document_id: int):
        """
        Clean up chunk files after processing is complete
        
        Args:
            document_id: ID of the document whose chunks to clean
        """
        try:
            chunk_pattern = f"doc_{document_id}_chunk_*.pdf"
            chunk_files = list(self.chunks_dir.glob(chunk_pattern))
            
            for chunk_file in chunk_files:
                try:
                    chunk_file.unlink()
                    logger.info(f"Deleted chunk file: {chunk_file}")
                except Exception as e:
                    logger.warning(f"Failed to delete chunk file {chunk_file}: {str(e)}")
            
            logger.info(f"Cleaned up {len(chunk_files)} chunk files for document {document_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up chunks for document {document_id}: {str(e)}")
    
    async def merge_chunk_results(self, 
                                chunks: List[DocumentChunk],
                                field_names: List[str]) -> dict:
        """
        Merge extraction results from all chunks into a single result
        
        Args:
            chunks: List of processed chunks
            field_names: List of field names that were extracted
            
        Returns:
            Merged extraction results
        """
        merged_result = {}
        
        for field_name in field_names:
            merged_result[field_name] = []
        
        # Collect all values from chunks
        for chunk in chunks:
            if chunk.extracted_data:
                for field_name in field_names:
                    if field_name in chunk.extracted_data:
                        value = chunk.extracted_data[field_name]
                        
                        # Handle both single values and lists
                        if isinstance(value, list):
                            merged_result[field_name].extend(value)
                        elif value is not None and value != '':
                            merged_result[field_name].append(value)
        
        # Deduplicate while preserving order
        for field_name in field_names:
            values = merged_result[field_name]
            if values:
                # Remove duplicates while preserving order
                seen = set()
                deduped = []
                for value in values:
                    if value not in seen:
                        seen.add(value)
                        deduped.append(value)
                merged_result[field_name] = deduped
            else:
                # No values found for this field
                merged_result[field_name] = []
        
        return merged_result