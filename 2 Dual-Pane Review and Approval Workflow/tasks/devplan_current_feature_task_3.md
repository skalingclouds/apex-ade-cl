# Implement Sidebar Navigation for Document Review

Implement a sidebar for navigating between documents and viewing their statuses.

Goals:
- Allow users to quickly switch between documents in the review queue.
- Display each document's current status in the sidebar.

Acceptance Criteria:
- Sidebar lists all documents available for review, with status indicators.
- Selecting a document loads it into the dual-pane review view.
- Sidebar updates in real time as statuses change.

Technical Details:
- Architecture/Module Changes: Add/extend frontend sidebar component. Backend endpoint to list documents and statuses.
- Interfaces and Types: Document list item includes ID, name, and status.
- Integration Points: Sidebar fetches document list from backend; listens for status updates.
- Side Effects/Dependencies: UI updates as statuses change.
- Examples/Conventions: Use dense layout and minimal styling per style guide.
- Testing: Include tests for navigation, status display, and real-time updates.

