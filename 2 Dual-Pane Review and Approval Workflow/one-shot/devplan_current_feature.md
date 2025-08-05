<!-- feature_id: cmdwfkc6000qp4ny82mnd638h -->

Implement the feature: Dual-Pane Review and Approval Workflow

This feature is part of the following context from the PRD:  
The system is an internal business tool for agentic PDF data extraction and review. Users upload PDFs, which are processed via the landing.ai SDK, and then review the results in a dual-pane interface: the original PDF on the left and extracted Markdown on the right. Users can approve, reject, or escalate documents, with workflow status managed in the backend and reflected in the UI. Sidebar navigation allows users to move between documents and see their statuses. The backend uses FastAPI and SQLite, and the frontend is built with React. Security, error handling, and GDPR compliance are required.

Feature Goals:
- Enable users to review the original PDF and extracted Markdown side by side.
- Allow users to approve, reject, or escalate document extraction results.
- Ensure document status is updated in both backend (SQLite) and frontend UI.
- Provide sidebar navigation for document browsing and status visibility.
- Enforce workflow rules (e.g., disable chat for rejected documents).
- Deliver clear, actionable feedback for all user actions and error states.

Feature Acceptance Criteria:
1. The frontend displays the original PDF (using PDF.js or similar) and extracted Markdown in a dual-pane layout.
2. Users can approve, reject, or escalate documents; actions update status in backend and UI.
3. Sidebar navigation lists documents and their statuses, allowing navigation between them.
4. Backend updates document status in SQLite and enforces workflow rules (e.g., disables chat on rejected docs).
5. UI provides clear, inline feedback on action success or failure.
6. If PDF rendering fails, a fallback message and download link are shown.
7. If extracted Markdown is missing, user is prompted to retry extraction.
8. If status update fails, error is displayed and user can retry.

Technical Details:

- Architecture/Module Changes:
  - **Frontend (React):**
    - Implement a dual-pane review component: left pane renders the PDF (PDF.js or React wrapper), right pane renders extracted Markdown (React Markdown library).
    - Add sidebar navigation component listing all documents with their statuses (pending, approved, rejected, escalated).
    - Integrate approval workflow controls (approve, reject, escalate) with clear UI feedback.
    - Ensure chat interface is disabled or hidden for rejected documents.
    - Handle error states for PDF rendering and Markdown extraction.
  - **Backend (FastAPI):**
    - Ensure endpoints for fetching PDF, Markdown, and document metadata are available:
      - `GET /api/documents/{id}/pdf`
      - `GET /api/documents/{id}/markdown`
      - `GET /api/documents/{id}` (metadata including status)
    - Implement endpoints for status updates:
      - `POST /api/documents/{id}/approve`
      - `POST /api/documents/{id}/reject`
      - `POST /api/documents/{id}/escalate`
    - Enforce workflow rules in endpoints (e.g., prevent chat on rejected docs).
    - Update SQLite `documents` table status field accordingly.

- Interfaces and Types:
  - **Document Metadata Example:**
    ```python
    class Document(BaseModel):
        id: int
        filename: str
        status: str  # pending, approved, rejected, escalated
        extracted_md: Optional[str]
        uploaded_at: datetime
        processed_at: Optional[datetime]
    ```
  - **Status Update Request/Response Example:**
    ```python
    class StatusUpdateResponse(BaseModel):
        success: bool
        message: str
        new_status: str
    ```
  - **Frontend Types:** Mirror backend types for document metadata and status.

- Integration Points:
  - Frontend fetches document list and metadata from `/api/documents` (or similar).
  - Fetches PDF and Markdown for selected document.
  - Sends status update requests to backend endpoints.
  - Backend updates SQLite and returns updated status.
  - Chat interface checks document status before enabling interaction.

- Database/Schema Changes:
  - No new schema changes required; ensure `status` field in `documents` table is updated on workflow actions.

- Side Effects/Dependencies:
  - UI disables or hides chat for rejected documents.
  - If PDF rendering fails, show fallback message and provide download link (use `/api/documents/{id}/pdf`).
  - If extracted Markdown is missing, prompt user to retry extraction (possibly via `/api/documents/{id}/extract`).
  - All status changes are logged and reflected in both UI and backend.

- Examples/Conventions:
  - Follow existing React component structure and styling conventions (dense, utility-focused, dark mode).
  - Use REST API patterns as described in the tech brief.
  - Use async/await and error boundaries in React for robust error handling.
  - Use Pydantic models for FastAPI request/response validation.

- Testing:
  - Include frontend tests for dual-pane rendering, sidebar navigation, and workflow actions (approve/reject/escalate).
  - Test backend endpoints for status updates, workflow enforcement, and error handling.
  - Test edge cases: PDF rendering failure, missing Markdown, failed status update.
  - Ensure chat is disabled for rejected documents.
  - Do not over-engineer; focus on critical paths and described edge cases.

- Security & Compliance:
  - Ensure all API calls are authenticated (if auth is enabled).
  - All status changes and document accesses are logged for audit.
  - Data is encrypted at rest and in transit as per project requirements.

- Analytics:
  - Ensure document status changes are tracked for analytics (number approved/rejected, etc.).

Implement this feature in alignment with the described architecture, API, and UI/UX conventions.