# Frontend: Add Export Options to Review View

Update the dual-pane review view to provide export options (CSV, Markdown) for each document. Show clear feedback on export success or failure, and allow retry if needed.

Goals:
- Enable users to easily export extracted data in their preferred format.
- Provide immediate feedback on export/download status.

Acceptance Criteria:
- Export buttons (CSV, Markdown) are visible in the review view.
- On click, triggers download from backend endpoints.
- If download fails, user is notified and can retry.
- UI feedback is clear and follows style guide (dense, utility-focused, inline feedback).

Technical Details:
- Architecture/Module Changes: Update review view component to include export controls.
- Interfaces and Types: Use existing document and user session types; add export status state.
- Integration Points: Connect to backend export endpoints with authentication.
- Side Effects/Dependencies: None beyond UI and API integration.
- Examples/Conventions: Follow button/link conventions and feedback patterns in the UI style guide.
- Testing: Add UI tests for export actions, feedback, and retry logic.
