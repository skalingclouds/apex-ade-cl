<!-- feature_id: cmdwfkc5n00ql4ny8blma39zt -->

Implement the feature: PDF Upload and Document Ingestion Workflow

This feature is part of the following context from the PRD:
The application is an internal business tool for agentic PDF data extraction, enabling users to upload PDFs for automated extraction and human-in-the-loop review. The upload workflow is the entry point for all subsequent processing, requiring robust validation, secure storage, and seamless integration with the extraction pipeline. The system must enforce a 50MB file size limit, accept only PDFs, and provide immediate, clear feedback to users. Uploaded PDFs are stored securely on the server, with metadata tracked in a SQLite database for further processing and review.

Feature Goals:
- Allow users to upload PDF files (≤50MB) via drag-and-drop or file picker in the frontend.
- Validate file type and size on both frontend and backend.
- Store uploaded PDFs on the server filesystem.
- Create a corresponding document record in the SQLite database.
- Return document ID and status to the frontend for further processing.
- Provide immediate, user-friendly feedback on upload progress and errors.
- Ensure uploaded PDFs are accessible for review and downstream extraction.

Feature Acceptance Criteria:
1. Frontend supports drag-and-drop and file picker for PDF uploads, with progress and error feedback.
2. Backend validates file type (PDF) and size (≤50MB), stores the file, and creates a DB record.
3. Upload endpoint returns document ID and status.
4. User receives clear error messages for invalid files or upload failures.
5. Uploaded PDFs are retrievable for review and further processing.

Technical Details:

- Architecture/Module Changes:
  - **Frontend (React):**
    - Implement a PDF upload component supporting drag-and-drop and file picker.
    - Integrate with the backend `/api/upload` endpoint via REST.
    - Display upload progress, success, and error states inline.
  - **Backend (FastAPI):**
    - Implement the `/api/upload` POST endpoint.
    - Validate incoming files for type (`application/pdf`) and size (≤50MB).
    - Store PDFs in a designated directory on the server filesystem.
    - Insert a new record into the `documents` table in SQLite with status (e.g., `pending`), filename, filepath, and timestamps.
    - Return JSON with document ID and status.

- Interfaces and Types:
  - **Frontend:** Use TypeScript interfaces for upload responses, e.g.:
    ```typescript
    interface UploadResponse {
      id: number;
      status: string;
    }
    ```
  - **Backend:** Pydantic models for response payloads, e.g.:
    ```python
    class UploadResponse(BaseModel):
        id: int
        status: str
    ```
  - **Database Schema:** Use the `documents` table as specified:
    - `id` (INTEGER PK)
    - `filename` (TEXT)
    - `filepath` (TEXT)
    - `status` (TEXT, e.g., 'pending')
    - `uploaded_at` (TIMESTAMP)
    - `processed_at` (TIMESTAMP, nullable)

- Integration Points:
  - **Frontend** calls `/api/upload` with the PDF file as `multipart/form-data`.
  - **Backend** stores the file, creates a DB record, and returns the document ID and status.
  - **Subsequent flows** (parse, extract, review) use the returned document ID.

- Database/Schema Changes:
  - No changes required; use the existing `documents` table as described in the tech brief.

- Side Effects/Dependencies:
  - PDFs are stored on the server filesystem in a secure, organized directory (e.g., `/data/pdfs/`).
  - Metadata is persisted in SQLite.
  - Ensure file and DB write operations are atomic—if storage fails, do not create a DB record.
  - All file and data storage must be encrypted at rest (per security requirements).
  - Ensure proper error handling and logging for failed uploads or storage errors.

- Examples/Conventions:
  - Follow existing React and FastAPI code patterns in the repository.
  - Use RESTful conventions for API design.
  - Use async/await patterns in FastAPI for non-blocking file IO.
  - Use environment variables or config files for storage paths and limits.

- Testing:
  - Include frontend tests for upload UI (drag-and-drop, file picker, error states).
  - Include backend tests for:
    - File type and size validation.
    - Successful storage and DB record creation.
    - Handling of invalid files and storage failures.
    - API response correctness.
  - Test edge cases: oversized files, non-PDF files, storage errors.

- Security:
  - Enforce HTTPS for all API calls.
  - Sanitize filenames and paths to prevent directory traversal.
  - Restrict access to internal users (basic auth or token, if enabled).
  - Encrypt files at rest and ensure secure file permissions.

- Analytics:
  - Increment "number of PDFs processed per user" metric upon successful upload.

- Edge Case Handling:
  - Reject files >50MB with a clear error message.
  - Reject non-PDF files with a prompt for valid PDF.
  - On storage failure, return a user-friendly error and do not create a DB record.

Proceed to implement this feature according to the above requirements, ensuring robust validation, secure storage, and seamless user experience for PDF uploads and ingestion.