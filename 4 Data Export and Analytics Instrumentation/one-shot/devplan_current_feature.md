<!-- feature_id: cmdwfkc6d00qt4ny8k0pauceo -->

Implement the feature: Data Export and Analytics Instrumentation

This feature is part of the following context from the PRD:  
The system is an internal business tool for agentic PDF data extraction, review, and approval, with a React frontend and FastAPI backend. Users upload PDFs, which are processed using the landing.ai SDK, and can review extracted data in a dual-pane interface. The tool must support exporting extracted data (CSV/Markdown) and track analytics on core user actions (uploads, approvals, rejections, chat interactions). Admins require access to basic usage metrics. Security, reliability, and clear user feedback are emphasized.

Feature Goals:
- Allow users to export extracted data for any document as CSV or Markdown via the frontend.
- Provide clear, actionable feedback to users on export success or failure.
- Log analytics events for uploads, approvals, rejections, and chat interactions.
- Enable admins to view aggregated usage metrics (PDFs processed, approval/rejection rates, chat frequency).
- Ensure robust error handling for export and analytics logging, with non-blocking failures.

Feature Acceptance Criteria:
1. Backend generates and serves CSV and Markdown exports for each document via download endpoints.
2. Frontend displays export options in the review view, with inline feedback on export status.
3. Analytics events are reliably logged for uploads, approvals, rejections, and chat interactions.
4. Admins can access a dashboard or endpoint showing usage metrics (PDFs processed, approval/rejection rates, chat frequency).
5. If export generation or analytics logging fails, users are notified and can retry; failures do not block core actions.

Technical Details:

- Architecture/Module Changes:
  - Backend: Extend FastAPI application to implement export endpoints and analytics logging. Add admin analytics endpoint.
  - Frontend: Update review view to include export controls and feedback UI. Add admin metrics view or page.
  - Ensure modular separation between export logic, analytics logging, and core document processing.

- Interfaces and Types:
  - Backend: Define response schemas for export endpoints (CSV, Markdown) and analytics endpoints (metrics summary).
  - Analytics event model: { event_type, document_id, user_id, timestamp, metadata }
  - Example metrics response: { pdfs_processed, approvals, rejections, escalations, chat_count, approval_rate, rejection_rate }

- Integration Points:
  - Export endpoints:
    - `GET /api/documents/{id}/export/csv` – returns CSV file for document.
    - `GET /api/documents/{id}/export/md` – returns Markdown file for document.
  - Analytics logging:
    - Log events on PDF upload, approval, rejection, escalation, and chat interaction.
    - Store analytics in a new or existing table (e.g., `analytics_events`) in SQLite.
  - Admin metrics:
    - `GET /api/analytics/metrics` – returns aggregated usage statistics for admin dashboard.
  - Frontend:
    - Add export buttons to review pane; call export endpoints and handle download.
    - Show inline feedback (success, failure, retry) for export actions.
    - Add admin metrics view/page, fetching from analytics endpoint.

- Database/Schema Changes:
  - Add table: `analytics_events`
    | Column        | Type       | Description                       |
    |---------------|------------|-----------------------------------|
    | id            | INTEGER PK | Unique event ID                   |
    | event_type    | TEXT       | (upload, approve, reject, escalate, chat) |
    | document_id   | INTEGER FK | Associated document               |
    | user_id       | TEXT       | (if available; else NULL)         |
    | timestamp     | TIMESTAMP  | Event time                        |
    | metadata      | TEXT/JSON  | Additional event data             |
  - No changes to `documents` or `chat_logs` tables unless required for metrics aggregation.

- Side Effects/Dependencies:
  - Export endpoints depend on successful extraction and storage of Markdown data.
  - Analytics logging should not block user actions; failures are logged for later review.
  - Admin metrics endpoint aggregates data from `documents`, `chat_logs`, and `analytics_events`.
  - Frontend export UI depends on review/approval workflow being present.

- Examples/Conventions:
  - Follow existing REST API patterns and error handling conventions in FastAPI backend.
  - Use standard Python libraries (`csv`, `io`, `markdown`) for export generation.
  - Frontend should use existing notification/toast or inline feedback components for user messages.
  - Maintain dense, utility-focused UI style as per PRD.

- Testing:
  - Backend: Add tests for export endpoints (valid/invalid document IDs, error cases), analytics event logging, and metrics aggregation.
  - Frontend: Add tests for export UI (button presence, feedback on success/failure), and admin metrics view.
  - Test edge cases: export failures, interrupted downloads, analytics logging failures, and retry flows.

- Security & Privacy:
  - Ensure export endpoints are protected (internal access/auth as per MVP).
  - Analytics data must not leak sensitive document content.
  - All endpoints must use HTTPS and sanitize user input.

- Other Notes:
  - If download is interrupted, frontend should allow user to retry.
  - If export fails (e.g., missing extracted data), return clear error and allow retry after reprocessing.
  - Analytics logging failures should be logged server-side for later investigation, but not block user actions.

Implement this feature in alignment with the above requirements, ensuring robust, user-friendly export and analytics capabilities integrated with the existing review and approval workflow.