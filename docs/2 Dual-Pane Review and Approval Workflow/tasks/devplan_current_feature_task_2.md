# Implement Approval Workflow Actions and Status Feedback

Implement approve, reject, and escalate actions in the review UI, with clear feedback and backend integration.

Goals:
- Allow users to approve, reject, or escalate the current document.
- Reflect status changes in the UI and persist them in the backend.
- Provide immediate, clear feedback on action success or failure.

Acceptance Criteria:
- Action buttons are visible and accessible in the UI.
- On action, status is updated in the backend (SQLite) and UI reflects the new status.
- If status update fails, display an error and allow retry.
- Workflow rules enforced (e.g., chat disabled for rejected docs).

Technical Details:
- Architecture/Module Changes: Add/extend backend endpoints for status updates. Update frontend to call these endpoints and handle responses.
- Interfaces and Types: Extend document type to include status and status history.
- Integration Points: Frontend calls backend API to update status; backend persists to SQLite.
- Database/Schema Changes: Ensure document status is stored and auditable in SQLite.
- Side Effects/Dependencies: UI disables/enables chat and actions based on status.
- Examples/Conventions: Use inline feedback and fast transitions per style guide.
- Testing: Include tests for status transitions, error handling, and workflow enforcement.

