"""
Optimized Chunk Processing Orchestrator
Leverages Landing.AI's built-in retry mechanism and parallel processing
"""
import asyncio
import logging
import time
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import json
from concurrent.futures import ThreadPoolExecutor

from app.models.document import Document, DocumentStatus
from app.models.document_chunk import (
    DocumentChunk, ChunkStatus, ProcessingLog, 
    ProcessingMetrics, ExtractionMethod
)
from app.services.simple_landing_ai_service import SimpleLandingAIService, ExtractionResult
from app.core.landing_ai_config import landing_ai_config

logger = logging.getLogger(__name__)

class OptimizedChunkProcessor:
    """
    Optimized chunk processor that leverages Landing.AI's built-in features:
    - Automatic retry with exponential backoff
    - Parallel processing with MAX_WORKERS
    - No redundant retry logic needed
    """
    
    def __init__(self, db: Session):
        """
        Initialize optimized chunk processor
        
        Args:
            db: Database session
        """
        self.db = db
        self.landing_ai_service = SimpleLandingAIService()
        
        # Use Landing.AI's MAX_WORKERS for parallel processing
        self.max_parallel_chunks = landing_ai_config.max_workers
        
        logger.info(f"OptimizedChunkProcessor initialized with {self.max_parallel_chunks} parallel workers")
    
    async def process_document_chunks(self,
                                     document: Document,
                                     selected_fields: List[str],
                                     custom_fields: Optional[List[dict]] = None) -> Dict[str, Any]:
        """
        Process all chunks for a document using Landing.AI's parallel processing
        
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
            
            # Estimate processing time
            time_estimate = landing_ai_config.estimate_processing_time(len(chunks))
            
            # Log start of processing
            self._log_processing_event(
                document_id=document.id,
                action="CHUNK_PROCESSING_START",
                message=f"Starting to process {len(chunks)} chunks with {self.max_parallel_chunks} parallel workers",
                metadata={
                    "total_chunks": len(chunks),
                    "parallel_workers": self.max_parallel_chunks,
                    "selected_fields": selected_fields,
                    "custom_fields": custom_fields,
                    "time_estimate": time_estimate
                }
            )
            
            # Process chunks in parallel batches
            results = await self._process_chunks_parallel(
                chunks=chunks,
                selected_fields=selected_fields,
                custom_fields=custom_fields
            )
            
            # Merge results from all chunks
            merged_results = await self._merge_chunk_results(
                chunks=chunks,
                field_names=selected_fields
            )
            
            # Update document with merged results
            document.extracted_data = json.dumps(merged_results)
            document.status = DocumentStatus.EXTRACTED
            document.completed_chunks = len([r for r in results if r is not None])
            self.db.commit()
            
            # Log completion
            self._log_processing_event(
                document_id=document.id,
                action="CHUNK_PROCESSING_COMPLETE",
                message=f"Successfully processed {len(results)}/{len(chunks)} chunks",
                metadata={
                    "successful_chunks": len([r for r in results if r is not None]),
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
    
    async def _process_chunks_parallel(self,
                                      chunks: List[DocumentChunk],
                                      selected_fields: List[str],
                                      custom_fields: Optional[List[dict]] = None) -> List[Optional[Dict]]:
        """
        Process chunks in parallel using Landing.AI's MAX_WORKERS setting
        
        Args:
            chunks: List of chunks to process
            selected_fields: Fields to extract
            custom_fields: Custom fields
            
        Returns:
            List of extraction results (None for failed chunks)
        """
        results = []
        
        # Process chunks in batches based on MAX_WORKERS
        batch_size = self.max_parallel_chunks
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_start = time.time()
            
            # Log batch start
            logger.info(f"Processing batch {i//batch_size + 1}: chunks {i+1}-{min(i+batch_size, len(chunks))}")
            
            # Process batch in parallel
            batch_tasks = []
            for chunk in batch:
                task = self._process_single_chunk_simplified(
                    chunk=chunk,
                    selected_fields=selected_fields,
                    custom_fields=custom_fields
                )
                batch_tasks.append(task)
            
            # Wait for batch to complete
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            # Log batch completion
            batch_time = time.time() - batch_start
            successful = len([r for r in batch_results if r and not isinstance(r, Exception)])
            logger.info(f"Batch completed in {batch_time:.2f}s: {successful}/{len(batch)} successful")
            
            # Add to overall results
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Chunk processing failed: {result}")
                    results.append(None)
                else:
                    results.append(result)
            
            # Update progress
            completed = len([r for r in results if r is not None])
            self._update_metrics(chunks[0].document_id, completed_chunks=completed)
        
        return results
    
    async def _process_single_chunk_simplified(self,
                                              chunk: DocumentChunk,
                                              selected_fields: List[str],
                                              custom_fields: Optional[List[dict]] = None) -> Optional[Dict[str, Any]]:
        """
        Process a single chunk - simplified version that relies on Landing.AI's retry mechanism
        
        Args:
            chunk: Chunk to process
            selected_fields: Fields to extract
            custom_fields: Custom fields to extract
            
        Returns:
            Extraction results for this chunk, or None if failed
        """
        start_time = time.time()
        
        # Update chunk status
        chunk.status = ChunkStatus.PROCESSING
        chunk.processing_started_at = datetime.utcnow()
        self.db.commit()
        
        try:
            # Log attempt
            self._log_processing_event(
                document_id=chunk.document_id,
                chunk_id=chunk.id,
                action="EXTRACTION_START",
                message=f"Processing chunk {chunk.chunk_number} (pages {chunk.start_page}-{chunk.end_page})",
                metadata={
                    "chunk_number": chunk.chunk_number,
                    "pages": f"{chunk.start_page}-{chunk.end_page}",
                    "file_size_mb": chunk.file_size_mb
                }
            )
            
            # Call extraction service - Landing.AI SDK handles retries automatically!
            extraction_result = await self.landing_ai_service.extract_document(
                file_path=chunk.file_path,
                selected_fields=selected_fields,
                custom_fields=custom_fields
            )
            
            # Check if we got results
            if extraction_result and extraction_result.data:
                processing_time_ms = int((time.time() - start_time) * 1000)
                
                # Determine extraction method from metadata
                extraction_method = extraction_result.metadata.get("extraction_method", "UNKNOWN")
                
                # Update chunk with results
                chunk.status = ChunkStatus.COMPLETED
                chunk.extracted_data = extraction_result.data
                chunk.extracted_fields = list(extraction_result.data.keys())
                chunk.extraction_method = extraction_method
                chunk.processing_completed_at = datetime.utcnow()
                chunk.processing_time_ms = processing_time_ms
                
                # Log successful extraction
                self._log_processing_event(
                    document_id=chunk.document_id,
                    chunk_id=chunk.id,
                    action="EXTRACTION_SUCCESS",
                    message=f"Successfully extracted {len(extraction_result.data)} fields using {extraction_method}",
                    extraction_method=extraction_method,
                    metadata={
                        "fields_extracted": list(extraction_result.data.keys()),
                        "processing_time_ms": processing_time_ms,
                        "method": extraction_method
                    }
                )
                
                # Update metrics
                self._update_extraction_method_count(chunk.document_id, extraction_method)
                
                self.db.commit()
                return extraction_result.data
            else:
                # No data extracted
                chunk.status = ChunkStatus.FAILED
                chunk.error_message = "No data extracted"
                self.db.commit()
                
                self._log_processing_event(
                    document_id=chunk.document_id,
                    chunk_id=chunk.id,
                    action="EXTRACTION_FAILED",
                    level="ERROR",
                    message="No data extracted from chunk"
                )
                
                return None
                
        except Exception as e:
            # Landing.AI SDK has already retried MAX_RETRIES times if we get here
            logger.error(f"Chunk {chunk.id} failed after all retries: {str(e)}")
            
            chunk.status = ChunkStatus.FAILED
            chunk.error_message = str(e)
            chunk.processing_completed_at = datetime.utcnow()
            self.db.commit()
            
            self._log_processing_event(
                document_id=chunk.document_id,
                chunk_id=chunk.id,
                action="EXTRACTION_FAILED",
                level="ERROR",
                message=f"Extraction failed after all retries: {str(e)}",
                metadata={"error": str(e)}
            )
            
            return None
    
    def _update_extraction_method_count(self, document_id: int, method: str):
        """Update extraction method usage in metrics"""
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
                
                # Log warning if OpenAI was used
                self._log_processing_event(
                    document_id=document_id,
                    action="OPENAI_FALLBACK_USED",
                    level="WARNING",
                    message="OpenAI fallback was used for extraction - consistency may vary",
                    extraction_method=ExtractionMethod.OPENAI_FALLBACK
                )
            
            self.db.commit()
    
    def _update_metrics(self, document_id: int, completed_chunks: Optional[int] = None):
        """Update processing metrics"""
        metrics = self.db.query(ProcessingMetrics).filter(
            ProcessingMetrics.document_id == document_id
        ).first()
        
        if metrics:
            if completed_chunks is not None:
                metrics.completed_chunks = completed_chunks
                metrics.processed_pages = self.db.query(DocumentChunk).filter(
                    DocumentChunk.document_id == document_id,
                    DocumentChunk.status == ChunkStatus.COMPLETED
                ).with_entities(DocumentChunk.page_count).scalar() or 0
            
            # Update completion status
            metrics.is_complete = (metrics.completed_chunks == metrics.total_chunks)
            metrics.updated_at = datetime.utcnow()
            
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
        """Log a processing event"""
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
        """Merge extraction results from all chunks"""
        merged = {}
        
        # Initialize fields
        for field in field_names:
            merged[field] = []
        
        # Collect values from successful chunks
        for chunk in chunks:
            if chunk.extracted_data and chunk.status == ChunkStatus.COMPLETED:
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