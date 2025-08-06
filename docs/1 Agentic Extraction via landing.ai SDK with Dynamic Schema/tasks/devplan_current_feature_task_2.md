# Frontend Display and Field Selection UI

Implement frontend components to display detected fields from the backend and allow users to select which fields to extract.

Goals:
- Provide a clear, interactive UI for users to review and select detected fields for extraction.

Acceptance Criteria:
- Detected fields are displayed in a list or table with relevant metadata.
- Users can select one or more fields (enforce at least one selection).
- If no fields are selected, prompt user to select at least one.
- User selections are sent to backend for schema generation and extraction.

Technical Details:
- Architecture/Module Changes: Add/extend frontend module for extraction workflow.
- Interfaces and Types: Define types for detected fields and user selections.
- Integration Points: Connect to backend endpoint for detected fields and submit selections to extraction endpoint.
- Side Effects/Dependencies: Depends on PDF upload and detected fields API.
- Examples/Conventions: Use dense, utility-focused UI with dark mode by default.
- Testing: Include tests for field display, selection logic, and validation feedback.
