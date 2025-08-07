"""
Landing.AI configuration management for optimal performance
Loads settings from environment variables to configure the SDK
"""
import os
from pathlib import Path
from typing import Optional
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class LandingAIConfig:
    """
    Manages Landing.AI SDK configuration for optimal performance
    Based on account rate limits and document characteristics
    """
    
    def __init__(self):
        # Load Landing.AI specific environment variables
        env_file = Path(__file__).parent.parent.parent / ".env.landing_ai"
        if env_file.exists():
            load_dotenv(env_file)
            logger.info(f"Loaded Landing.AI config from {env_file}")
        
        # Batch processing settings
        self.batch_size = int(os.getenv("BATCH_SIZE", "1"))
        self.max_workers = int(os.getenv("MAX_WORKERS", "5"))
        
        # Retry settings
        self.max_retries = int(os.getenv("MAX_RETRIES", "50"))
        self.max_retry_wait_time = int(os.getenv("MAX_RETRY_WAIT_TIME", "30"))
        self.retry_logging_style = os.getenv("RETRY_LOGGING_STYLE", "inline_block")
        
        # Calculate effective parallelism
        self.max_parallelism = self.batch_size * self.max_workers
        
        # Ensure we don't exceed Landing.AI's max parallelism limit
        if self.max_parallelism > 100:
            logger.warning(f"Max parallelism {self.max_parallelism} exceeds limit of 100")
            # Adjust settings to stay under limit
            self.max_workers = min(self.max_workers, 100 // self.batch_size)
            self.max_parallelism = self.batch_size * self.max_workers
            logger.info(f"Adjusted max_workers to {self.max_workers}")
    
    def apply_to_environment(self):
        """Apply configuration to environment variables for SDK to use"""
        os.environ["BATCH_SIZE"] = str(self.batch_size)
        os.environ["MAX_WORKERS"] = str(self.max_workers)
        os.environ["MAX_RETRIES"] = str(self.max_retries)
        os.environ["MAX_RETRY_WAIT_TIME"] = str(self.max_retry_wait_time)
        os.environ["RETRY_LOGGING_STYLE"] = self.retry_logging_style
        
        logger.info(f"Applied Landing.AI config: batch_size={self.batch_size}, "
                   f"max_workers={self.max_workers}, max_parallelism={self.max_parallelism}")
    
    def get_optimal_settings(self, rate_limit: int, avg_latency_seconds: float) -> dict:
        """
        Calculate optimal settings based on rate limit and latency
        
        Args:
            rate_limit: Requests per minute allowed
            avg_latency_seconds: Average time per request in seconds
            
        Returns:
            Dict with optimal batch_size and max_workers
        """
        # Calculate how many requests can be in flight
        requests_per_second = rate_limit / 60
        max_concurrent = int(requests_per_second * avg_latency_seconds * 1.5)  # 1.5x for safety
        
        # For large documents, prefer single document with multiple workers
        if max_concurrent <= 5:
            return {"batch_size": 1, "max_workers": max_concurrent}
        elif max_concurrent <= 20:
            return {"batch_size": 2, "max_workers": max_concurrent // 2}
        else:
            return {"batch_size": 4, "max_workers": min(max_concurrent // 4, 25)}
    
    def estimate_processing_time(self, 
                                total_chunks: int,
                                avg_chunk_time_seconds: float = 15) -> dict:
        """
        Estimate processing time for a document
        
        Args:
            total_chunks: Number of chunks to process
            avg_chunk_time_seconds: Average time per chunk
            
        Returns:
            Dict with time estimates
        """
        # Calculate batches needed
        chunks_per_batch = self.max_workers
        total_batches = (total_chunks + chunks_per_batch - 1) // chunks_per_batch
        
        # Calculate time estimates
        ideal_time = total_batches * avg_chunk_time_seconds
        with_overhead = ideal_time * 1.3  # 30% overhead for retries, network, etc.
        worst_case = ideal_time * 2.0  # 100% overhead for heavy retries
        
        return {
            "total_chunks": total_chunks,
            "parallel_workers": self.max_workers,
            "total_batches": total_batches,
            "ideal_seconds": ideal_time,
            "expected_seconds": with_overhead,
            "worst_case_seconds": worst_case,
            "ideal_minutes": ideal_time / 60,
            "expected_minutes": with_overhead / 60,
            "worst_case_minutes": worst_case / 60
        }

# Global config instance
landing_ai_config = LandingAIConfig()

# Apply configuration on module import
landing_ai_config.apply_to_environment()