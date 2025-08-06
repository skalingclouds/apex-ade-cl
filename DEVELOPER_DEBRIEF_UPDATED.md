# Developer Debrief: Apex ADE Landing.AI Integration (Updated)

## Project Overview
Apex ADE is a document processing application that integrates with Landing.AI's agentic document parsing service. The application allows users to upload PDF documents, parse them to identify fields, extract structured data, and review/approve the results with a human-in-the-loop workflow.

## Current System Architecture

### Backend (FastAPI + SQLAlchemy)
- **Framework**: FastAPI with async support
- **Database**: SQLite with SQLAlchemy ORM
- **File Storage**: Local filesystem in `./uploads` directory
- **API Integration**: Landing.AI SDK (`agentic_doc` package)
- **Processing**: Enhanced markdown processor for clean output
- **Dependencies**: BeautifulSoup4, lxml for HTML parsing

### Frontend (React + TypeScript)
- **Framework**: React with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Query
- **HTTP Client**: Axios
- **PDF Viewer**: Custom PDFViewer component with full controls
- **Markdown Rendering**: ReactMarkdown with remark-gfm

### Key Components
1. **Document Upload**: Handles PDF file uploads with progress tracking
2. **Document Parsing**: Uses Landing.AI to analyze document structure and extract markdown
3. **Field Selection**: Dynamic UI for selecting fields to extract
4. **Data Extraction**: Extracts structured data using dynamically generated Pydantic schemas
5. **Review Interface**: Dual-pane view with enhanced PDF controls and clean markdown display
6. **Export Functionality**: Clean exports to CSV, Markdown, and Plain Text formats
7. **Audit & Analytics**: Comprehensive logging of all document operations

## ✅ Current Implementation Status (All Major Features Working)

### ✅ Fully Working Features

#### 1. Document Upload & Processing
- PDF upload with progress tracking
- Automatic status management through workflow states
- Error handling with retry capabilities
- File validation and size limits

#### 2. Landing.AI Integration
- **API Key Management**: Properly configured as `VISION_AGENT_API_KEY`
- **Parse Endpoint**: Successfully extracts markdown and suggests fields
- **Extract Endpoint**: Uses dynamic Pydantic schemas for data extraction
- **Error Handling**: Comprehensive error catching and user feedback

#### 3. Markdown Processing & Display
- **Clean Rendering**: All Landing.AI artifacts removed (HTML comments, IDs, metadata)
- **Table Support**: Proper HTML to markdown table conversion
- **Display Quality**: Tables render cleanly matching Landing.AI playground
- **Enhanced Processor**: `LandingAIMarkdownProcessor` class handles all edge cases

#### 4. Export Functionality
- **CSV Export**: Pure CSV with no markdown/HTML artifacts, Excel-ready
- **Markdown Export**: Clean markdown with proper formatting preserved
- **Plain Text Export**: All formatting removed for clean text output
- **PDF Download**: Direct access to original PDF

#### 5. PDF Viewer Controls
- **Zoom**: In/out controls with percentage display (50% - 200%)
- **Rotation**: Clockwise and counter-clockwise rotation
- **Navigation**: Page-by-page navigation with current page indicator
- **Fit to Width**: Automatic width adjustment
- **Highlights**: Support for highlighting areas from chat responses
- **Download**: Direct PDF download button

#### 6. Review Interface
- **Dual-Pane Layout**: PDF on left, extracted content on right
- **Action Buttons**: Approve, Reject, Escalate with reasons
- **Status Indicators**: Clear visual feedback for document status
- **Sidebar Navigation**: Browse through multiple documents
- **Chat Integration**: Context-aware chat for document queries

#### 7. Audit & Analytics
- **Audit Logging**: All document actions tracked
- **Analytics Events**: Document lifecycle events logged
- **Export Tracking**: Export actions and formats logged
- **Performance Metrics**: Processing times and success rates

## Technical Implementation Details

### Landing.AI SDK Integration

The integration follows a two-step process:

1. **Parse Phase**: 
```python
# Uses SimpleLandingAIService
result = await parse(
    documents=[file_path],
    include_marginalia=True,
    include_metadata_in_markdown=True
)
# Returns: markdown content and suggested fields
```

2. **Extract Phase**:
```python
# Dynamic Pydantic model created from selected fields
result = await parse(
    documents=[file_path],
    extraction_model=DynamicModel
)
# Returns: structured data based on schema
```

### API Key Configuration

The Landing.AI SDK requires `VISION_AGENT_API_KEY` environment variable:

1. **Settings Configuration** (`app/core/config.py`):
```python
VISION_AGENT_API_KEY: str = ""  # Loaded from .env
```

2. **Service Initialization** (all Landing.AI services):
```python
def __init__(self):
    self.api_key = settings.VISION_AGENT_API_KEY
    if self.api_key:
        os.environ['VISION_AGENT_API_KEY'] = self.api_key
```

3. **Environment File** (`.env`):
```
VISION_AGENT_API_KEY=your-api-key-here
```

### Markdown Processing Pipeline

1. **Raw Landing.AI Output** → Contains HTML comments, IDs, metadata
2. **LandingAIMarkdownProcessor.clean_markdown_for_display()** → Removes artifacts
3. **HTML Table Conversion** → Converts `<table>` to markdown tables
4. **Normalization** → Ensures consistent table formatting
5. **Frontend Display** → ReactMarkdown with custom components

### Export Processing

#### CSV Export:
```python
LandingAIMarkdownProcessor.extract_clean_csv_data()
# 1. Extracts tables from markdown
# 2. Removes all formatting
# 3. Produces pure CSV string
```

#### Markdown Export:
```python
LandingAIMarkdownProcessor.format_for_markdown_export()
# 1. Cleans Landing.AI artifacts
# 2. Preserves markdown formatting
# 3. Adds proper spacing
```

#### Plain Text Export:
```python
LandingAIMarkdownProcessor.extract_plain_text()
# 1. Removes all markdown syntax
# 2. Converts tables to tab-separated
# 3. Returns pure text
```

## File Structure

```
apex-ade-cl/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints/
│   │   │       ├── extraction.py  # Parse/Extract endpoints
│   │   │       ├── export.py      # Export endpoints (CSV, MD, TXT)
│   │   │       └── documents.py   # Document CRUD
│   │   ├── services/
│   │   │   ├── landing_ai_service.py        # Main Landing.AI service
│   │   │   ├── simple_landing_ai_service.py # Simplified implementation
│   │   │   └── audit_service.py             # Audit logging
│   │   └── utils/
│   │       ├── enhanced_markdown_processor.py # New processor
│   │       └── markdown_processor.py          # Legacy processor
│   └── .env  # Contains VISION_AGENT_API_KEY
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── PDFViewer.tsx      # Enhanced PDF viewer
│   │   │   └── FieldSelector.tsx  # Field selection UI
│   │   ├── pages/
│   │   │   └── DocumentReview.tsx # Main review interface
│   │   └── utils/
│   │       ├── enhancedMarkdownUtils.ts # Frontend markdown processing
│   │       └── markdownUtils.ts         # Legacy utilities
│   └── package.json  # Includes @react-pdf-viewer packages
```

## Recent Fixes and Improvements

### 1. API Key Issue Resolution
- **Problem**: "API key is invalid" errors
- **Cause**: Mismatch between `LANDING_AI_API_KEY` (backend) and `VISION_AGENT_API_KEY` (SDK)
- **Solution**: Renamed all references to `VISION_AGENT_API_KEY` and explicitly set environment variable

### 2. Table Rendering Issues
- **Problem**: Tables displayed with HTML artifacts and Landing.AI metadata
- **Cause**: Raw markdown from Landing.AI contains HTML comments and IDs
- **Solution**: Created `LandingAIMarkdownProcessor` with comprehensive cleaning

### 3. Export Quality
- **Problem**: CSV exports contained markdown syntax, not Excel-compatible
- **Cause**: Simple regex replacements insufficient for complex markdown
- **Solution**: Proper table extraction and conversion to pure CSV

### 4. PDF Viewer Limitations
- **Problem**: No zoom or rotation controls
- **Cause**: Basic react-pdf implementation
- **Solution**: Custom `PDFViewer` component with full controls

## How to Run

### Backend Setup:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file with:
# VISION_AGENT_API_KEY=your-landing-ai-api-key

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup:
```bash
cd frontend
npm install
npm run dev  # Development server on http://localhost:3000
```

## API Endpoints

### Core Endpoints:
- `POST /api/v1/documents/{id}/parse` - Parse document for fields
- `POST /api/v1/documents/{id}/extract` - Extract data with schema
- `GET /api/v1/documents/{id}/export/csv` - Export as CSV
- `GET /api/v1/documents/{id}/export/markdown` - Export as Markdown
- `GET /api/v1/documents/{id}/export/text` - Export as Plain Text
- `POST /api/v1/documents/{id}/approve` - Approve document
- `POST /api/v1/documents/{id}/reject` - Reject document

## Document Status Workflow

```
PENDING → PARSING → PARSED → EXTRACTING → EXTRACTED → APPROVED/REJECTED
                                    ↓
                                 FAILED (with retry option)
```

## Key Dependencies

### Backend:
- FastAPI 0.104.1
- SQLAlchemy 2.0.23
- agentic-doc 0.3.1 (Landing.AI SDK)
- beautifulsoup4 4.13.4
- lxml 6.0.0
- pydantic 2.5.2

### Frontend:
- React 18.2.0
- TypeScript 5.2.2
- react-pdf 7.7.0
- @react-pdf-viewer/core 3.12.0
- react-markdown 9.0.1
- remark-gfm 4.0.0
- axios 1.6.2
- tailwindcss 3.3.6

## Testing

### Manual Testing Checklist:
- [x] Upload PDF document
- [x] Parse document (check markdown display)
- [x] Select fields for extraction
- [x] Extract data (verify in UI)
- [x] Export to CSV (import to Excel)
- [x] Export to Markdown (check formatting)
- [x] Export to Plain Text (verify no artifacts)
- [x] Approve/Reject documents
- [x] PDF zoom and rotation controls
- [x] Chat functionality with highlights

### Known Edge Cases Handled:
- Landing.AI HTML comments in markdown
- HTML tables mixed with markdown
- Colspan attributes in tables
- Multi-page PDF navigation
- Large markdown content rendering
- Special characters in CSV export

## Performance Optimizations

1. **Async Processing**: All Landing.AI calls use `asyncio.run_in_executor`
2. **Caching**: Markdown cleaned once and cached for display
3. **Lazy Loading**: Documents loaded on demand
4. **Batch Operations**: Multiple exports can run concurrently
5. **Status Polling**: Efficient polling only during processing states

## Security Considerations

1. **API Key Protection**: Never exposed to frontend
2. **File Validation**: Upload size and type restrictions
3. **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
4. **XSS Prevention**: React's built-in escaping
5. **CORS Configuration**: Restricted to specific origins

## Future Enhancements

1. **Batch Processing**: Upload and process multiple PDFs
2. **Custom Field Templates**: Save and reuse field configurations
3. **Advanced Analytics**: Processing metrics dashboard
4. **Webhook Integration**: Notify external systems on completion
5. **Cloud Storage**: S3/Azure blob storage for PDFs
6. **Authentication**: User management and access control
7. **Rate Limiting**: API throttling for Landing.AI calls

## Troubleshooting

### Common Issues:

1. **"API key is invalid"**
   - Ensure `VISION_AGENT_API_KEY` is set in `.env`
   - Restart backend server after changing `.env`

2. **Tables not rendering properly**
   - Check if `remark-gfm` is installed
   - Verify `ReactMarkdown` components are configured

3. **CSV export has formatting issues**
   - Ensure `beautifulsoup4` and `lxml` are installed
   - Check `enhanced_markdown_processor.py` is being used

4. **PDF viewer not working**
   - Verify `@react-pdf-viewer` packages installed
   - Check browser console for CORS issues

## Support

For issues or questions:
- Review error logs in `backend/backend.log`
- Check browser console for frontend errors
- Ensure all dependencies are installed
- Verify Landing.AI API key is valid

## License

[Your License Here]

---
*Last Updated: August 2025*
*Document Version: 2.0*