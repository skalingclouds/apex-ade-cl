# CLAUDE.md - Apex ADE CL Project

This file provides guidance to Claude Code (claude.ai/code) when working with the Apex ADE CL project.

## Project Overview
Apex ADE CL is a document extraction system that processes PDF documents (including large 900MB+ files) using Landing.AI's Agentic Document Extraction API. It supports both chunked processing for large documents and direct processing for smaller ones.

## Critical Known Issues and Fixes

### 1. DocumentStatus Enum Errors
**Issue**: `AttributeError: PROCESSING` - Using non-existent enum values
**Fix**: Use correct enum values from `app/models/document.py`:
- ✅ Use: `DocumentStatus.EXTRACTING`, `DocumentStatus.PENDING`, `DocumentStatus.EXTRACTED`
- ❌ Don't use: `DocumentStatus.PROCESSING` (doesn't exist)

### 2. Small Document Extraction Fails ("No chunks found")
**Issue**: System tries to find chunks for ALL documents, even non-chunked ones
**Fix**: Check `document.is_chunked` flag before looking for chunks:
```python
if not document.is_chunked:
    # Process original file directly
    result = await landing_ai_service.extract_document(file_path=document.filepath, ...)
else:
    # Process chunks
    chunks = db.query(DocumentChunk).filter(...)
```

### 3. Custom Field Extraction Not Working
**Issue**: Custom fields like "Apex ID" aren't being processed
**Fix**: The `/process` endpoint must accept `ExtractionRequest` body:
```python
@router.post("/{document_id}/process")
async def process_document(extraction_request: ExtractionRequest, ...):
    # Access fields via extraction_request.selected_fields and extraction_request.custom_fields
```

### 4. Multiple Fields Selected But Only One Returned
**Issue**: UI shows only first field even when multiple are selected
**Fix**: Backend returns fields as arrays. Frontend must handle array display:
```javascript
// Handle array values properly
if (Array.isArray(value) && value.length > 0) {
    displayValue = value.length === 1 ? value[0] : value.join(', ')
}
```

### 5. UI Flow Issues (Blank Screen, No Progress Indicators)
**Issue**: Modal closes immediately after clicking extract, no progress shown
**Fix**: 
- Keep modal open during extraction with loading overlay
- Poll for status updates instead of assuming immediate success
- Add visual feedback (spinners, progress messages)

## Architecture Overview

### Document Processing Flow
1. **Small Documents (<40MB)**: 
   - Upload → Status: PENDING → Parse → Extract → EXTRACTED
   - No chunking, direct processing

2. **Large Documents (>40MB)**:
   - Upload → Auto-chunk (45 pages) → Status: PENDING
   - Parse (uses first chunk) → Extract (all chunks parallel) → EXTRACTED

### Key Services

#### `SimpleLandingAIService`
- Handles Landing.AI API integration
- Methods:
  - `extract_document()` - Main extraction with field selection
  - `extract_with_structured_model()` - Uses Pydantic models
  - `_extract_using_landing_ai_api()` - Direct API calls

#### `OptimizedChunkProcessor`
- Manages chunked document processing
- Handles both chunked and non-chunked documents
- Parallel processing with configurable workers

#### `PDFChunker`
- Splits large PDFs into 45-page chunks
- Manages chunk storage and tracking

## Configuration

### Critical Settings
```python
# Chunk size (pages) - reduced from 50 for safety
CHUNK_SIZE = 45

# File size threshold for chunking (MB)
CHUNK_THRESHOLD_MB = 40

# Landing.AI API settings
VISION_AGENT_API_KEY = os.getenv("VISION_AGENT_API_KEY")
```

## Common Development Tasks

### Testing Extraction
```python
# Test with custom fields
custom_fields = [
    {'name': 'Apex ID', 'type': 'string', 'description': 'Unique Apex identifier'}
]
selected_fields = ['claimant_name', 'claim_number']
```

### Debugging Extraction Issues
1. Check backend logs for field extraction:
   ```
   logger.info(f"Selected fields: {selected_fields}")
   logger.info(f"Extracted data: {extracted_data}")
   ```

2. Verify document status transitions:
   - PENDING → PARSING → EXTRACTING → EXTRACTED

3. Check chunk processing for large docs:
   - Look for chunk creation logs
   - Verify parallel processing

## Testing Endpoints

### Parse Document (Get Fields)
```bash
POST /api/v1/documents/{id}/parse
# Returns available fields from OptInFormExtraction model
```

### Process Document (Extract)
```bash
POST /api/v1/documents/{id}/process
Body: {
  "selected_fields": ["field1", "field2"],
  "custom_fields": [{"name": "Custom", "type": "string"}]
}
```

## Frontend Components

### FieldSelector
- Shows available fields with checkboxes
- Supports custom field addition
- Must show loading state during extraction

### DocumentReview
- Main document view page
- Handles extraction flow
- Displays results with proper array handling

### ProgressIndicator
- Shows status-specific messages and animations
- Three states: parsing, extracting, processing
- Includes time estimates and progress descriptions

### ExtractedResultsDisplay
- **Table View**: Clean HTML table with sortable columns
- **List View**: Card-based display for each field
- **Markdown View**: Rendered markdown with proper styling
- **Pagination**: Handles large datasets efficiently (50 items/page)
- **Array Handling**: Expandable arrays with item counts

## Deployment Notes

- Backend requires `VISION_AGENT_API_KEY` environment variable
- Frontend needs proper CORS configuration
- Database migrations required for chunk tables

## Troubleshooting

### "No chunks found" Error
- Check if document.is_chunked flag is set correctly
- Verify chunk creation in uploads/chunks/ directory

### Empty Extraction Results
- Check Landing.AI API response in logs
- Verify field names match document content
- Check if using correct extraction method (API vs SDK)

### UI Not Updating
- Ensure polling is active during extraction
- Check WebSocket connections if applicable
- Verify status transitions in database

### 400 Errors on /process Endpoint
- Usually means document is already being processed
- Backend now handles gracefully by returning current status
- Frontend polls for completion

### Toast Errors
- Use `toast.loading()` not `toast.info()` (doesn't exist in react-hot-toast)
- Always dismiss loading toasts with `toast.dismiss(toastId)`

### Large Dataset Handling (3000+ pages)
- ExtractedResultsDisplay component handles pagination (50 items/page)
- Three view modes: Table, List, Markdown
- Array values are expandable/collapsible
- Performance optimized with virtualization

## Performance Expectations
- **Parse operations**: Typically take 30-60 seconds
- **Extraction**: Can take 1-2 minutes for large documents
- **Large documents (900MB+)**: May take 3-5 minutes total
- **Chunking**: Happens during upload, adds 10-30 seconds

## Important Notes
- ALWAYS test with both small (2-page) and large (900MB+) documents
- Custom fields must be properly typed in the JSON schema
- The 45-page chunk limit is critical for Landing.AI API limits
- Monitor API usage to avoid rate limits
- Visual feedback is critical - users need to see progress
- Always handle both chunked and non-chunked documents