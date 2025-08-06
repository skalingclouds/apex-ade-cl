Current feature/project:  
Agentic Human Extraction Form – Internal Business Tool for PDF Extraction, Review, and Chat (Full System Implementation)

This request is part of the following context from the PRD:  
Develop an internal web tool for business analysts and data processors to upload PDFs, extract structured data using the landing.ai SDK, review results in a dual-pane interface, approve/reject/escalate documents, and interact with an AI agent via chat with contextual PDF highlighting. The system must support secure storage, analytics, and GDPR-compliant deletion, with a dense, utility-focused UI and robust backend integration.

Goals:
- Enable users to upload PDFs (≤50MB) via drag-and-drop or file picker.
- Process PDFs using landing.ai SDK (parse/extract), allowing user-driven field selection and dynamic schema generation.
- Present a dual-pane review interface: original PDF (left), extracted Markdown (right).
- Support document approval workflow (approve/reject/escalate) with sidebar navigation.
- Provide a chat interface for document Q&A, with PDF highlights for referenced answers.
- Store PDFs and extracted data securely (encrypted at rest/in transit), persist metadata and chat logs in SQLite.
- Allow export of extracted data as CSV/Markdown.
- Instrument analytics for uploads, approvals, rejections, and chat frequency.
- Enforce GDPR-compliant data deletion.
- Restrict access to authenticated internal users.

Acceptance Criteria:
- Monorepo with clear separation of React frontend and FastAPI backend.
- All REST API endpoints stubbed and implemented as per API design.
- SQLite schema includes `documents` and `chat_logs` tables as specified.
- Local file storage for PDFs and extracted data, with encryption at rest.
- Frontend supports PDF upload (drag-and-drop/file picker), dual-pane review, sidebar navigation, approval actions, and chat with contextual highlighting.
- Backend integrates with landing.ai SDK for parse/extract, supports dynamic Pydantic schema generation.
- All user actions (upload, approve, reject, escalate, chat, export) are logged for analytics.
- Export endpoints provide CSV and Markdown downloads.
- Authentication is enforced for all endpoints.
- GDPR-compliant deletion endpoint removes PDFs and DB records.
- Error handling and user feedback for all edge cases (file size/type, extraction failure, chat errors, etc.).
- UI follows dense, dark-mode, utility-focused style with fast transitions and inline feedback.
- Tests cover critical backend and frontend flows, including upload, extraction, review, approval, chat, and export.

Technical Details:

**Architecture/Module Changes:**
- Monorepo structure:  
  - `/frontend` (React app)  
  - `/backend` (FastAPI app)  
- Backend modules:  
  - `api/` (all REST endpoints)  
  - `models/` (Pydantic models, dynamic schema generation)  
  - `db/` (SQLite integration, ORM or raw SQL)  
  - `storage/` (file storage, encryption utilities)  
  - `analytics/` (event logging)  
  - `auth/` (basic or token-based authentication)
- Frontend modules:  
  - `components/` (PDF upload, dual-pane review, sidebar, chat, export controls)  
  - `state/` (global state management, e.g., Redux or Context)  
  - `api/` (REST API client)  
  - `styles/` (dark mode, dense layout, utility classes)

**Interfaces and Types:**
- Document object:  
  - `id: int`, `filename: str`, `filepath: str`, `status: str`, `extracted_md: str`, `uploaded_at: datetime`, `processed_at: datetime`
- Chat log object:  
  - `id: int`, `document_id: int`, `query: str`, `response: str`, `created_at: datetime`
- API request/response types as per endpoints (see API Design in tech brief).
- Dynamic Pydantic models for extraction schemas (see tech brief for example).

**Integration Points:**
- Backend ↔ landing.ai SDK:  
  - Use `parse_document` and `extract_document` methods as shown in tech brief.
- Frontend ↔ Backend:  
  - All user actions (upload, review, chat, export) via REST API.
- PDF rendering:  
  - Use PDF.js or React wrapper for in-browser display.
- Markdown rendering:  
  - Use React Markdown library for extracted content.
- Chat:  
  - Frontend chat component sends queries to `/api/documents/{id}/chat`, displays responses and triggers PDF highlights.

**Database/Schema Changes:**
- Implement `documents` and `chat_logs` tables as specified in tech brief.
- Ensure all fields (including status, extracted_md, timestamps) are present.
- Support for deletion of records and associated files for GDPR compliance.

**Side Effects/Dependencies:**
- All PDFs and extracted data must be encrypted at rest.
- All API communication must be over HTTPS.
- Authentication required for all endpoints; block access if misconfigured.
- If database or storage initialization fails, log error and halt startup.
- If file upload fails (size/type/storage), return actionable error to user.
- If extraction or SDK call fails, mark document as failed, notify user, and allow retry/escalation.
- If chat or highlight mapping fails, show fallback response and log issue.
- If export or analytics logging fails, notify user but do not block main action.

**Examples/Conventions:**
- Follow React and FastAPI best practices for component and endpoint structure.
- Use async/await for all I/O and SDK calls in backend.
- Use utility-first CSS or CSS-in-JS for dense, dark-mode UI.
- Use consistent error and success feedback patterns in UI.
- Use RESTful conventions for all API endpoints.

**Testing:**
- Backend:  
  - Unit tests for all endpoints (upload, parse, extract, review, chat, export, delete).
  - Integration tests for landing.ai SDK calls (mocked where needed).
  - Tests for authentication, encryption, and error handling.
- Frontend:  
  - Component tests for upload, review, chat, and export flows.
  - E2E tests for critical user journeys (upload → extract → review → approve/reject → export).
- Focus tests on critical paths and edge cases as described in PRD; do not over-engineer.

**Other Important Areas:**
- Analytics:  
  - Log events for uploads, approvals, rejections, escalations, and chat interactions.
  - Provide admin endpoint/UI for viewing core metrics (PDFs processed, approval/rejection rates, chat frequency).
- Security:  
  - Sanitize all user inputs.
  - Ensure encryption at rest and in transit.
  - Implement GDPR-compliant deletion endpoint.
- Scalability:  
  - Design backend for async processing and modularity to allow future scaling.
- Accessibility:  
  - Ensure UI is navigable via keyboard and screen readers where feasible.

**Instructions for AI agent:**
- Implement only what is described in the PRD, feature list, and tech brief.
- Do not introduce new features, endpoints, or architectural changes beyond what is specified.
- Use the provided API design, database schema, and integration patterns.
- Adhere to the dense, utility-focused, dark-mode UI style.
- Ensure all flows are robust to edge cases and provide actionable feedback to users.
- Follow existing patterns and conventions in the repository if present; otherwise, use standard best practices for React and FastAPI projects.

This prompt covers the full implementation scope for the agentic PDF extraction tool as described in the provided documents.