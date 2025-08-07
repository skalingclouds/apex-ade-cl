"""
Chunk Processing Orchestrator
Handles processing of document chunks with rate limiting, retries, and consistent output
"""
import asyncio
import logging
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json

from app.models.document import Document, DocumentStatus
from app.models.document_chunk import (
    DocumentChunk, ChunkStatus, ProcessingLog, 
    ProcessingMetrics, ExtractionMethod
)
from app.services.simple_landing_ai_service import SimpleLandingAIService
from app.schemas.extraction import ExtractionResult

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter for API calls"""
    
    def __init__(self, max_rpm: int):
        """
        Initialize rate limiter
        
        Args:
            max_rpm: Maximum requests per minute
        """
        self.max_rpm = max_rpm
        self.min_interval = 60.0 / max_rpm  # Minimum seconds between requests
        self.last_request_time = 0
        self.request_times = []
    
    async def wait_if_needed(self):
        """Wait if necessary to respect rate limits"""
        current_time = time.time()
        
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if current_time - t < 60]
        
        # Check if we're at the limit
        if len(self.request_times) >= self.max_rpm:
            # Calculate how long to wait
            oldest_request = self.request_times[0]
            wait_time = 60 - (current_time - oldest_request) + 0.1  # Add small buffer
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.request_times.append(time.time())

class ChunkProcessor:
    """
    Orchestrates the processing of document chunks with resilience and consistency
    """
    
    def __init__(self, db: Session):
        """
        Initialize chunk processor
        
        Args:
            db: Database session
        """
        self.db = db
        self.landing_ai_service = SimpleLandingAIService()
        
        # Rate limiters for different APIs (Paid plan limits)
        self.landing_ai_limiter = RateLimiter(max_rpm=25)  # Landing.AI Paid: 25 requests/minute
        self.openai_limiter = RateLimiter(max_rpm=50)  # OpenAI: 50 requests/minute
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay_base = 2  # Exponential backoff base
    
    async def process_document_chunks(self,
                                     document: Document,
                                     selected_fields: List[str],
                                     custom_fields: Optional[List[dict]] = None) -> Dict[str, Any]:
        """
        Process all chunks for a document
        
        Args:
            document: Document to process
            selected_fields: Fields to extract
            custom_fields: Custom fields to extract
            
        Returns:
            Merged extraction results
        """
        try:
            # Update document status
            document.status = DocumentStatus.CHUNK_PROCESSING
            self.db.commit()
            
            # Get all chunks
            chunks = self.db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document.id
            ).order_by(DocumentChunk.chunk_number).all()
            
            if not chunks:
                raise ValueError(f"No chunks found for document {document.id}")
            
            # Log start of processing
            self._log_processing_event(
                document_id=document.id,
                action="CHUNK_PROCESSING_START",
                message=f"Starting to process {len(chunks)} chunks",
                metadata={
                    "total_chunks": len(chunks),
                    "selected_fields": selected_fields,
                    "custom_fields": custom_fields
                }
            )
            
            # Process chunks sequentially (can be made parallel with semaphore)
            results = []
            for chunk in chunks:
                try:
                    result = await self._process_single_chunk(
                        chunk=chunk,
                        selected_fields=selected_fields,
                        custom_fields=custom_fields
                    )
                    results.append(result)
                    
                    # Update progress
                    document.completed_chunks = len(results)
                    self._update_metrics(document.id)
                    self.db.commit()
                    
                except Exception as e:
                    logger.error(f"Failed to process chunk {chunk.id}: {str(e)}")
                    # Continue with other chunks even if one fails
                    continue
            
            # Merge results from all chunks
            merged_results = await self._merge_chunk_results(
                chunks=chunks,
                field_names=selected_fields
            )
            
            # Update document with merged results
            document.extracted_data = json.dumps(merged_results)
            document.status = DocumentStatus.EXTRACTED
            self.db.commit()
            
            # Log completion
            self._log_processing_event(
                document_id=document.id,
                action="CHUNK_PROCESSING_COMPLETE",
                message=f"Successfully processed {len(results)}/{len(chunks)} chunks",
                metadata={
                    "successful_chunks": len(results),
                    "total_chunks": len(chunks),
                    "merged_fields": list(merged_results.keys())
                }
            )
            
            return merged_results
            
        except Exception as e:
            logger.error(f"Error processing document chunks: {str(e)}")
            document.status = DocumentStatus.FAILED
            document.error_message = str(e)
            self.db.commit()
            raise
    
    async def _process_single_chunk(self,
                                   chunk: DocumentChunk,
                                   selected_fields: List[str],
                                   custom_fields: Optional[List[dict]] = None) -> Dict[str, Any]:
        """
        Process a single chunk with retries and fallbacks
        
        Args:
            chunk: Chunk to process
            selected_fields: Fields to extract
            custom_fields: Custom fields to extract
            
        Returns:
            Extraction results for this chunk
        """
        start_time = time.time()
        
        # Update chunk status
        chunk.status = ChunkStatus.PROCESSING
        chunk.processing_started_at = datetime.utcnow()
        self.db.commit()
        
        extraction_result = None
        extraction_method_used = None
        
        for attempt in range(self.max_retries):
            try:
                # Log attempt
                self._log_processing_event(
                    document_id=chunk.document_id,
                    chunk_id=chunk.id,
                    action="EXTRACTION_ATTEMPT",
                    message=f"Processing chunk {chunk.chunk_number} (attempt {attempt + 1})",
                    metadata={
                        "chunk_number": chunk.chunk_number,
                        "pages": f"{chunk.start_page}-{chunk.end_page}",
                        "attempt": attempt + 1
                    }
                )
                
                # Try extraction with Landing.AI (with rate limiting)
                await self.landing_ai_limiter.wait_if_needed()
                
                # Call the extraction service
                extraction_result = await self.landing_ai_service.extract_document(
                    file_path=chunk.file_path,
                    selected_fields=selected_fields,
                    custom_fields=custom_fields
                )
                
                # Determine which method was actually used
                extraction_method_used = self._determine_extraction_method(extraction_result)
                
                # If we got results, break the retry loop
                if extraction_result and extraction_result.data:
                    break
                    
            except Exception as e:
                logger.error(f"Extraction attempt {attempt + 1} failed for chunk {chunk.id}: {str(e)}")
                
                # Log the failure
                self._log_processing_event(
                    document_id=chunk.document_id,
                    chunk_id=chunk.id,
                    action="EXTRACTION_FAILED",
                    level="ERROR",
                    message=f"Extraction attempt {attempt + 1} failed: {str(e)}",
                    metadata={"error": str(e), "attempt": attempt + 1}
                )
                
                # If this was the last attempt, mark as failed
                if attempt == self.max_retries - 1:
                    chunk.status = ChunkStatus.FAILED
                    chunk.error_message = str(e)
                    chunk.retry_count = attempt + 1
                    self.db.commit()
                    raise
                
                # Wait before retrying (exponential backoff)
                wait_time = self.retry_delay_base ** attempt
                await asyncio.sleep(wait_time)
        
        # Process successful extraction
        if extraction_result and extraction_result.data:
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Update chunk with results
            chunk.status = ChunkStatus.COMPLETED
            chunk.extracted_data = extraction_result.data
            chunk.extracted_fields = list(extraction_result.data.keys())
            chunk.extraction_method = extraction_method_used
            chunk.processing_completed_at = datetime.utcnow()
            chunk.processing_time_ms = processing_time_ms
            chunk.retry_count = attempt + 1
            
            # Log successful extraction
            self._log_processing_event(
                document_id=chunk.document_id,
                chunk_id=chunk.id,
                action="EXTRACTION_SUCCESS",
                message=f"Successfully extracted {len(extraction_result.data)} fields using {extraction_method_used}",
                extraction_method=extraction_method_used,
                metadata={
                    "fields_extracted": list(extraction_result.data.keys()),
                    "processing_time_ms": processing_time_ms,
                    "method": extraction_method_used
                }
            )
            
            # Update metrics based on extraction method
            self._update_extraction_method_count(chunk.document_id, extraction_method_used)
            
            self.db.commit()
            return extraction_result.data
        else:
            # No data extracted
            chunk.status = ChunkStatus.FAILED
            chunk.error_message = "No data extracted"
            self.db.commit()
            return {}
    
    def _determine_extraction_method(self, result: ExtractionResult) -> str:
        """
        Determine which extraction method was actually used based on the result
        
        Args:
            result: Extraction result
            
        Returns:
            ExtractionMethod enum value
        """
        # Check result metadata for hints about which method was used
        if result and hasattr(result, 'metadata'):
            method = result.metadata.get('extraction_method')
            if method:
                return method
        
        # Default to Landing.AI API if we can't determine
        return ExtractionMethod.LANDING_AI_API
    
    def _update_extraction_method_count(self, document_id: int, method: str):
        """
        Update the metrics table with extraction method usage
        
        Args:
            document_id: Document ID
            method: Extraction method used
        """
        metrics = self.db.query(ProcessingMetrics).filter(
            ProcessingMetrics.document_id == document_id
        ).first()
        
        if metrics:
            if method == ExtractionMethod.LANDING_AI_API:
                metrics.landing_ai_api_count += 1
            elif method == ExtractionMethod.LANDING_AI_SDK:
                metrics.landing_ai_sdk_count += 1
            elif method == ExtractionMethod.OPENAI_FALLBACK:
                metrics.openai_fallback_count += 1
                
                # Log warning if OpenAI was used (last resort)
                self._log_processing_event(
                    document_id=document_id,
                    action="OPENAI_FALLBACK_USED",
                    level="WARNING",
                    message="OpenAI fallback was used for extraction",
                    extraction_method=ExtractionMethod.OPENAI_FALLBACK
                )
            
            self.db.commit()
    
    def _update_metrics(self, document_id: int):
        """
        Update processing metrics for the document
        
        Args:
            document_id: Document ID
        """
        metrics = self.db.query(ProcessingMetrics).filter(
            ProcessingMetrics.document_id == document_id
        ).first()
        
        if metrics:
            # Count completed and failed chunks
            chunks = self.db.query(DocumentChunk).filter(
                DocumentChunk.document_id == document_id
            ).all()
            
            completed = sum(1 for c in chunks if c.status == ChunkStatus.COMPLETED)
            failed = sum(1 for c in chunks if c.status == ChunkStatus.FAILED)
            
            metrics.completed_chunks = completed
            metrics.failed_chunks = failed
            metrics.processed_pages = sum(c.page_count for c in chunks if c.status == ChunkStatus.COMPLETED)
            
            # Calculate average processing time
            processing_times = [c.processing_time_ms for c in chunks 
                              if c.processing_time_ms is not None]
            if processing_times:
                metrics.avg_chunk_time_ms = sum(processing_times) / len(processing_times)
                metrics.total_processing_time_ms = sum(processing_times)
            
            # Update completion status
            metrics.is_complete = (completed == metrics.total_chunks)
            metrics.has_failures = (failed > 0)
            
            if metrics.is_complete:
                metrics.actual_completion = datetime.utcnow()
            
            self.db.commit()
    
    def _log_processing_event(self,
                             document_id: int,
                             action: str,
                             message: str,
                             chunk_id: Optional[int] = None,
                             level: str = "INFO",
                             extraction_method: Optional[str] = None,
                             metadata: Optional[Dict] = None):
        """
        Log a processing event to the database
        
        Args:
            document_id: Document ID
            action: Action being performed
            message: Log message
            chunk_id: Optional chunk ID
            level: Log level
            extraction_method: Method used for extraction
            metadata: Additional metadata
        """
        log_entry = ProcessingLog(
            document_id=document_id,
            chunk_id=chunk_id,
            action=action,
            level=level,
            message=message,
            extraction_method=extraction_method,
            log_metadata=metadata or {}
        )
        self.db.add(log_entry)
        self.db.commit()
    
    async def _merge_chunk_results(self,
                                  chunks: List[DocumentChunk],
                                  field_names: List[str]) -> Dict[str, Any]:
        """
        Merge extraction results from all chunks
        
        Args:
            chunks: List of processed chunks
            field_names: Field names to merge
            
        Returns:
            Merged results
        """
        merged = {}
        
        # Initialize fields
        for field in field_names:
            merged[field] = []
        
        # Collect values from all chunks
        for chunk in chunks:
            if chunk.extracted_data:
                for field in field_names:
                    if field in chunk.extracted_data:
                        value = chunk.extracted_data[field]
                        if isinstance(value, list):
                            merged[field].extend(value)
                        elif value:
                            merged[field].append(value)
        
        # Deduplicate values while preserving order
        for field in field_names:
            values = merged[field]
            if values:
                # Remove duplicates
                seen = set()
                deduped = []
                for v in values:
                    if v not in seen:
                        seen.add(v)
                        deduped.append(v)
                merged[field] = deduped
        
        return merged