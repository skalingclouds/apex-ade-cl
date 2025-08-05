# Implement Dual-Pane Review UI Layout

Implement the dual-pane review interface for document review.

Goals:
- Display the original PDF and extracted Markdown side by side for comparison.
- Ensure the layout is dense, utility-focused, and defaults to dark mode.

Acceptance Criteria:
- Left pane renders the PDF (using PDF.js or similar).
- Right pane displays extracted Markdown in a read-only format.
- Responsive layout with minimal decorative elements.
- If PDF rendering fails, show a fallback message and provide a download link.
- If extracted Markdown is missing, prompt user to retry extraction.

Technical Details:
- Architecture/Module Changes: Add/extend frontend components for dual-pane layout. Integrate PDF.js (or equivalent) for PDF rendering and a Markdown renderer for the extracted content.
- Interfaces and Types: Define types for document, extraction result, and status.
- Integration Points: Fetch PDF and Markdown from backend endpoints.
- Side Effects/Dependencies: UI updates for error/fallback states.
- Examples/Conventions: Follow existing frontend component and styling conventions. Use solid buttons for primary actions.
- Testing: Include tests for rendering, error states, and fallback UI.

