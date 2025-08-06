<!-- feature_id: cmdwfkc5u00qn4ny8egli3e2v -->

Implement the feature: Agentic Extraction via landing.ai SDK with Dynamic Schema

This feature is part of the following context from the PRD:  
The system is an internal business tool for extracting structured data from PDFs using the landing.ai SDK. Users upload PDFs, which are parsed to detect extractable fields. Users select which fields to extract, and the backend dynamically generates a schema for extraction. Extracted data is validated, stored, and presented for human review. The process must be robust, user-friendly, and support error handling and escalation. The backend is Python (FastAPI), and the frontend is React. Data is stored on the local filesystem and in SQLite.

Feature Goals:
- Integrate the landing.ai SDK to parse uploaded PDFs and detect extractable fields.
- Present detected fields to users in the frontend for selection.
- Dynamically generate a Pydantic schema on the backend based on user-selected fields.
- Extract structured data using the generated schema and store validated results.
- Handle extraction errors gracefully, providing clear feedback and options to retry or escalate.

Feature Acceptance Criteria:
1. Backend integrates with landing.ai SDK to call the parse endpoint and returns detected fields to the frontend.
2. Frontend displays detected fields and allows user selection for extraction.
3. Backend generates a Pydantic schema at runtime based on user-selected fields.
4. Backend calls the extract endpoint with the generated schema and stores validated results.
5. Extraction errors are handled gracefully, with clear feedback and option to retry or escalate.

Technical Details:

- Backend Integration:
  - Use the landing.ai Python SDK to call the `parse` endpoint on uploaded PDFs.
  - Expose a POST endpoint (`/api/documents/{id}/parse`) that triggers parsing and returns detected fields.
  - Expose a POST endpoint (`/api/documents/{id}/extract`) that accepts user-selected fields, generates a dynamic Pydantic schema, and calls the SDK's `extract` endpoint.
  - Store extracted data (Markdown) and update document status in the SQLite `documents` table.
  - On SDK or extraction errors, mark the document as failed and return a clear error message to the frontend.
  - Log errors and support retry or escalation via dedicated endpoints.

- Frontend Integration:
  - After PDF upload, call the parse endpoint and display detected fields in a selection UI.
  - Require the user to select at least one field before proceeding.
  - On submission, send selected fields to the extract endpoint and display extraction progress/status.
  - On extraction success, update the review UI with extracted Markdown.
  - On error, display clear feedback and provide options to retry extraction or escalate the document.

- Architecture/Module Changes:
  - Backend: Add/extend FastAPI endpoints for `/api/documents/{id}/parse` and `/api/documents/{id}/extract`.
  - Backend: Implement dynamic Pydantic schema generation based on user input.
  - Backend: Integrate error handling and document status updates (pending, failed, escalated).
  - Frontend: Add UI components for field selection and extraction status feedback.

- Interfaces and Types:
  - Backend: Define request/response models for parse and extract endpoints (e.g., list of fields, selected fields).
  - Backend: Use Pydantic's `create_model` for dynamic schema generation.
  - Frontend: Define types for detected fields and extraction requests.

- Integration Points:
  - Backend <-> landing.ai SDK: For parse and extract operations.
  - Backend <-> SQLite: For storing document metadata, extraction results, and status.
  - Backend <-> Frontend: REST API for parse, extract, and status updates.

- Database/Schema Changes:
  - No new tables required; use the existing `documents` table to store extraction status and extracted Markdown.
  - Update `status` and `extracted_md` columns as extraction progresses.

- Side Effects/Dependencies:
  - Extraction is dependent on successful PDF upload and ingestion.
  - Extraction errors must update document status and trigger frontend feedback.
  - Extraction results must be available for review and export.

- Examples/Conventions:
  - Follow existing FastAPI and React code patterns in the repository.
  - Use async endpoints and error handling conventions as established in the backend.
  - UI should match the dense, utility-focused style with inline feedback.

- Testing:
  - Backend: Add tests for parse and extract endpoints, including dynamic schema generation and error cases.
  - Frontend: Add tests for field selection UI, extraction workflow, and error feedback.
  - Test edge cases: SDK failure, no fields selected, schema mismatch, and retry/escalate flows.

- Other Important Areas:
  - Enforce max file size (50MB) at both frontend and backend.
  - Ensure all user input is sanitized and validated.
  - All API communication must be over HTTPS.
  - Ensure GDPR compliance for data handling and deletion.

This implementation should enable robust, user-driven agentic extraction of structured data from PDFs, leveraging the landing.ai SDK and dynamic schema generation, with a seamless and error-tolerant workflow.