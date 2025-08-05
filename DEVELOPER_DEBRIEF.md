# Developer Debrief: Apex ADE Landing.AI Integration

## Project Overview
Apex ADE is a document processing application that integrates with Landing.AI's agentic document parsing service. The application allows users to upload PDF documents, parse them to identify fields, extract structured data, and review/approve the results.

## Current System Architecture

### Backend (FastAPI + SQLAlchemy)
- **Framework**: FastAPI with async support
- **Database**: SQLite with SQLAlchemy ORM
- **File Storage**: Local filesystem in `./uploads` directory
- **API Integration**: Landing.AI SDK (`agentic_doc` package)

### Frontend (React + TypeScript)
- **Framework**: React with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Query
- **HTTP Client**: Axios

### Key Components
1. **Document Upload**: Handles PDF file uploads with progress tracking
2. **Document Parsing**: Uses Landing.AI to analyze document structure
3. **Field Selection**: Dynamic UI for selecting fields to extract
4. **Data Extraction**: Extracts structured data using dynamically generated Pydantic schemas
5. **Review Interface**: Dual-pane view with PDF preview and extracted content
6. **Export Functionality**: Export to CSV and Markdown formats

## Current Implementation Status

### ✅ Working Features
1. **File Upload**: Successfully uploads PDFs to backend
2. **Basic UI**: All pages render correctly
3. **Database**: Properly stores document metadata and status
4. **Authentication**: API key configured for Landing.AI
5. **Field Detection**: Parse endpoint returns available fields
6. **Dynamic Schema Generation**: Creates Pydantic models based on selected fields

### ❌ Current Issues

#### 1. ParseResponse Schema Mismatch
**Error**: `"ParseResponse" object has no field "markdown"`
**Location**: Backend parse endpoint
**Issue**: The Pydantic model validation is failing even though we've added the markdown field to the schema

**Current Code**:
```python
# app/schemas/extraction.py
class ParseResponse(BaseModel):
    fields: List[FieldInfo]
    document_type: Optional[str] = None
    confidence: Optional[float] = None
    markdown: Optional[str] = None  # This was added but error persists
```

**Possible Cause**: The backend server may not have reloaded properly after the schema change

#### 2. Markdown Endpoint 400 Error
**Error**: `Failed to load resource: the server responded with a status of 400 (Bad Request)`
**Endpoint**: `/api/v1/documents/20/markdown`
**Issue**: The markdown content is not being saved during parse, so the endpoint returns "No extracted markdown available"

### Landing.AI Integration Details

Based on the developer documentation review, the proper workflow is:

1. **Parse without extraction model**: 
   ```python
   result = parse(
       documents=[file_path],
       include_marginalia=True,
       include_metadata_in_markdown=True
   )
   # Access: result[0].markdown, result[0].chunks
   ```

2. **Parse with extraction model** (separate call):
   ```python
   result_fe = parse(
       documents=[file_path], 
       extraction_model=Product  # Pydantic model
   )
   # Access: result_fe[0].extraction, result_fe[0].extraction_metadata
   ```

### Current Implementation Challenges

1. **Two-Step Process**: The documentation shows parsing and extraction as two separate API calls, but our implementation tries to do extraction in one step with a dynamically created schema

2. **Markdown Storage**: The markdown content from the initial parse needs to be properly stored in the database before extraction

3. **Schema Validation**: The ParseResponse Pydantic model validation is strict and may be caching the old schema

## Immediate Action Items

1. **Restart Backend Server**: Force restart to ensure schema changes are loaded
   ```bash
   pkill -9 -f uvicorn
   cd backend && source venv/bin/activate
   VISION_AGENT_API_KEY=<key> uvicorn app.main:app --reload
   ```

2. **Consider Splitting Parse/Extract**: Based on Landing.AI docs, consider implementing:
   - Parse endpoint: Just parse and save markdown
   - Extract endpoint: Use the saved document with extraction model

3. **Debug Schema Loading**: Add logging to verify the ParseResponse schema is correctly loaded:
   ```python
   import logging
   from app.schemas.extraction import ParseResponse
   logging.info(f"ParseResponse fields: {ParseResponse.__fields__}")
   ```

4. **Verify API Key**: Ensure VISION_AGENT_API_KEY environment variable is set when starting the server

## Environment Variables Required
```bash
# Backend .env
LANDING_AI_API_KEY=MmhtN2t2enA1bHM1aWRhdnU5emVsOmljRlc4ZzdPd2J1bDgyUGZOeEZ1UWRldVVyY1ozODJz
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Runtime environment
export VISION_AGENT_API_KEY=MmhtN2t2enA1bHM1aWRhdnU5emVsOmljRlc4ZzdPd2J1bDgyUGZOeEZ1UWRldVVyY1ozODJz
```

## Testing Workflow
1. Upload a PDF document
2. Navigate to `/documents/{id}`
3. Click "Parse" button
4. Wait for parsing to complete (shows field selector)
5. Select fields and click "Extract"
6. Review extracted data

## Known Working Endpoints
- `GET /api/v1/documents/` - List documents
- `POST /api/v1/documents/upload` - Upload PDF
- `GET /api/v1/documents/{id}` - Get document details
- `GET /api/v1/documents/{id}/pdf` - Get PDF file

## Problematic Endpoints
- `POST /api/v1/documents/{id}/parse` - ParseResponse schema issue
- `GET /api/v1/documents/{id}/markdown` - No markdown available
- `POST /api/v1/documents/{id}/extract` - Depends on parse working

## Next Steps for Resolution

1. **Immediate**: Restart backend with proper environment variables
2. **Short-term**: Fix ParseResponse schema validation issue
3. **Medium-term**: Refactor to match Landing.AI's two-step parse/extract pattern
4. **Long-term**: Add proper error handling and retry mechanisms

## Developer Notes
- The Landing.AI SDK expects `VISION_AGENT_API_KEY` as an environment variable
- The parse function returns a list of ParsedDocument objects
- Markdown is available on parsed_doc.markdown
- Extraction requires a predefined Pydantic model
- The backend uses hot-reload, but Pydantic models may cache
- The parse function should be called with keyword arguments, not a config object

## Recent Fixes Applied (2025-08-05)

### 1. Fixed Landing.AI parse function call
Changed from:
```python
parse(documents=[file_path], config=config)
```
To:
```python
parse(documents=[file_path], include_marginalia=True, include_metadata_in_markdown=True)
```

### 2. Server restart command
```bash
pkill -9 -f uvicorn
cd backend && source venv/bin/activate
VISION_AGENT_API_KEY=MmhtN2t2enA1bHM1aWRhdnU5emVsOmljRlc4ZzdPd2J1bDgyUGZOeEZ1UWRldVVyY1ozODJz uvicorn app.main:app --reload
```

---
*Last Updated: 2025-08-05*
*Issue Status: Server restarted with fixes - awaiting test of parse endpoint*