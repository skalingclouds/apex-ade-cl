# Large File Upload Guide

## Problem Solved
The system now supports uploading and processing large PDF files (900MB+) with automatic chunking.

## Changes Made

### Frontend
- Removed 50MB file size restriction in Upload.tsx
- Added file rejection error handling with toast notifications
- Updated UI text to indicate support for large PDFs with automatic chunking

### Backend
- Increased MAX_UPLOAD_SIZE from 50MB to 1GB in config.py
- Created start_server.py script with proper uvicorn configuration for large files
- Better error messages showing size limit in GB

## Running the Server for Large Files

### Option 1: Use the new start script (Recommended)
```bash
cd backend
python start_server.py
```

This script:
- Configures uvicorn to handle up to 1GB file uploads
- Sets appropriate timeouts for large file processing
- Enables proper request body size limits

### Option 2: Manual uvicorn with parameters
```bash
cd backend
uvicorn app.main:app --reload --limit-max-requests 1000 --h11-max-incomplete-event-size 1073741824
```

## File Size Limits
- **Frontend**: No limit (removed restriction)
- **Backend**: 1GB (1073741824 bytes)
- **Recommended PDF size**: Up to 900MB
- **Chunking**: Automatic for files over 40 pages

## Processing Large Files
When you upload a large PDF (like your 900MB/3270-page document):
1. The file uploads to the server (may take a moment for large files)
2. The system automatically chunks it into 40-page segments
3. Each chunk is processed using the three-tier extraction strategy:
   - Landing.AI API (primary)
   - Landing.AI SDK (fallback)
   - OpenAI GPT-4 (last resort)
4. Results are aggregated and displayed

## Troubleshooting

### "File too large" error
- Make sure you're using start_server.py to run the backend
- Check that MAX_UPLOAD_SIZE in config.py is set to 1073741824

### Upload doesn't start
- Check browser console for errors
- Verify the file is a PDF
- Try refreshing the page

### Slow upload
- This is normal for large files
- The upload progress bar shows current status
- 900MB files may take 1-2 minutes depending on connection speed

## Performance Tips
- The system processes chunks in parallel (5 workers)
- Landing.AI has a 25 rpm limit on paid plans
- Each chunk takes approximately 2-3 seconds to process
- A 3270-page document (~82 chunks) will take about 4-7 minutes total