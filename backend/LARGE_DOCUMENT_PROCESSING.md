# Large Document Processing Guide

## Overview
This system is optimized for processing massive documents (900MB+, 3000+ pages) using Landing.AI's paid plan features with intelligent chunking and automatic retry handling.

## Key Features

### 1. Landing.AI Built-in Retry Mechanism
The Landing.AI SDK **automatically handles** retries for you:
- **Automatic retry** for HTTP errors: 408, 429, 502, 503, 504
- **Exponential backoff** with jitter (up to 10 seconds)
- **No manual retry code needed** - the SDK handles everything
- **Configurable** via environment variables

### 2. Optimized Configuration (Paid Plan)

#### Rate Limits
- **API Rate Limit**: 25 requests/minute
- **Page Limits**: 50 pages max per extraction
- **Parallel Processing**: Up to 5 chunks simultaneously

#### Optimal Settings (.env.landing_ai)
```bash
BATCH_SIZE=1           # Process one document at a time
MAX_WORKERS=5          # 5 parallel chunks
MAX_RETRIES=50         # Retry attempts (reduced from default 100)
MAX_RETRY_WAIT_TIME=30 # Max wait between retries
RETRY_LOGGING_STYLE=inline_block  # Progress blocks instead of verbose logs
```

### 3. Chunk Size Optimization
- **Default**: 40 pages per chunk (safe under 50-page limit)
- **Dynamic adjustment**: 10-45 pages based on content
- **Heavy pages**: Automatically reduced chunk size

## Processing Flow

### 1. Document Chunking
```python
# Automatic chunking for large documents
if document.page_count > 100 or document.file_size_mb > 50:
    chunks = PDFChunker(max_pages_per_chunk=40).create_chunks(document)
```

### 2. Parallel Processing
```
Document (3270 pages) → 82 chunks @ 40 pages each
    ↓
Batch 1: Chunks 1-5   (parallel) ← MAX_WORKERS=5
Batch 2: Chunks 6-10  (parallel)
Batch 3: Chunks 11-15 (parallel)
... (17 total batches)
    ↓
Merged Results
```

### 3. Extraction Priority
```
1. Landing.AI SDK (preferred) → Unlimited parsing, 50-page extraction
2. Landing.AI API (fallback)  → 50-page limit
3. OpenAI (last resort)        → Logged as WARNING
```

## Performance Expectations

### 900MB / 3270-Page Document
| Metric | Value |
|--------|-------|
| Chunks | 82 @ 40 pages |
| Parallel Workers | 5 |
| Total Batches | 17 |
| Ideal Time | ~4.25 minutes |
| Expected Time | ~8-10 minutes |
| With Heavy Retries | ~15 minutes |

### Time Calculation
```
82 chunks ÷ 5 parallel = 17 batches
17 batches × 15 sec/batch = 255 seconds
With overhead (30%): ~330 seconds = 5.5 minutes
With retries: ~8-10 minutes typical
```

## API Usage

### 1. Create Chunks
```bash
POST /api/documents/{id}/chunk
```
Response:
```json
{
  "total_chunks": 82,
  "page_count": 3270,
  "file_size_mb": 900
}
```

### 2. Process Chunks
```bash
POST /api/documents/{id}/process-chunks
{
  "selected_fields": ["apex_id", "date", "amount"],
  "custom_fields": []
}
```

### 3. Monitor Progress
```bash
GET /api/documents/{id}/progress
```
Response:
```json
{
  "progress": {
    "percentage": 45.5,
    "completed_chunks": 37,
    "total_chunks": 82
  },
  "performance": {
    "avg_chunk_time_ms": 15000,
    "time_remaining_seconds": 450
  },
  "extraction_methods": {
    "landing_ai_sdk": 35,
    "landing_ai_api": 2,
    "openai_fallback": 0
  }
}
```

## Monitoring & Logging

### Extraction Method Tracking
Each chunk logs which method successfully extracted data:
```sql
SELECT extraction_method, COUNT(*) 
FROM document_chunks 
WHERE document_id = ? 
GROUP BY extraction_method;
```

### Processing Logs
```bash
GET /api/documents/{id}/logs?level=WARNING
```
Shows any OpenAI fallback usage (consistency concerns).

### Retry Visualization
With `RETRY_LOGGING_STYLE=inline_block`:
```
Processing chunk 15... ███ (3 retries)
Processing chunk 16... █ (1 retry)
Processing chunk 17... ✓ (no retries)
```

## Troubleshooting

### Issue: Rate Limit Errors
**Solution**: Already handled by SDK! If persistent:
```bash
# Reduce parallel workers
MAX_WORKERS=3
```

### Issue: Slow Processing
**Check**:
1. Average page size: `file_size_mb / page_count`
2. If > 0.5 MB/page, chunks auto-reduce to 25 pages

### Issue: OpenAI Fallback Warnings
**Meaning**: Landing.AI methods failed, using OpenAI (less consistent)
**Action**: Check Landing.AI API status, verify API key

### Issue: Memory Usage
**Solution**: Processing is sequential by batch, memory stays < 500MB

## Best Practices

### 1. Pre-Processing Checks
```python
# Check if chunking is needed
should_chunk, page_count, size_mb = chunker.should_chunk_document(file_path)
```

### 2. Field Selection
- Use multi-value fields for repeating data: `apex_id`, `date`, `invoice_number`
- Single-value fields for summary data: `total_amount`, `document_type`

### 3. Custom Fields
Add fields the AI might miss:
```json
{
  "custom_fields": [
    {"name": "special_code", "type": "string", "description": "Custom tracking code"}
  ]
}
```

### 4. Cleanup
After processing:
```bash
DELETE /api/documents/{id}/chunks  # Removes chunk files
```

## Configuration Files

### Required Files
1. `.env` - Main configuration with API keys
2. `.env.landing_ai` - Landing.AI specific settings
3. `alembic.ini` - Database migrations

### Environment Variables
```bash
# .env
VISION_AGENT_API_KEY=your_landing_ai_key
OPENAI_API_KEY=your_openai_key

# .env.landing_ai  
BATCH_SIZE=1
MAX_WORKERS=5
MAX_RETRIES=50
MAX_RETRY_WAIT_TIME=30
RETRY_LOGGING_STYLE=inline_block
```

## Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Copy and configure .env files
cp .env.example .env
cp .env.landing_ai.example .env.landing_ai
```

### 2. Process Large Document
```python
from app.services.pdf_chunker import PDFChunker
from app.services.chunk_processor_optimized import OptimizedChunkProcessor

# Create chunks
chunker = PDFChunker()
chunks = await chunker.create_chunks(document, db)

# Process with optimal settings
processor = OptimizedChunkProcessor(db)
results = await processor.process_document_chunks(
    document, 
    selected_fields=["apex_id", "date"],
    custom_fields=[]
)
```

## Summary

This system leverages Landing.AI's built-in features for optimal performance:
- **No manual retry code** - SDK handles it automatically
- **Parallel processing** - 5 chunks simultaneously  
- **Smart chunking** - 40 pages default, adjusts for content
- **Full audit trail** - Every extraction method logged
- **8-10 minute processing** for 3000+ page documents

The key insight: Let Landing.AI's SDK handle the complexity (retries, parallelism) while we focus on optimal configuration and monitoring.