# Develop Frontend Chat Component with PDF Highlight Integration

Develop the frontend chat UI component that allows users to send queries and view AI responses, and integrates with the PDF viewer to highlight referenced sections based on AI-provided metadata.

Goals:
- Provide a seamless chat interface for document Q&A.
- Visually highlight relevant PDF sections in response to AI answers.
- Disable chat if the document is rejected.

Acceptance Criteria:
- Users can send chat queries and view AI responses in real time.
- When a response includes highlight metadata, the PDF viewer highlights the specified regions.
- If no highlight is provided, the chat response is still shown.
- Chat input is disabled and a message is shown if the document is rejected.

Technical Details:
- Architecture/Module Changes: Add/extend chat UI component; integrate with PDF viewer component for highlight overlays.
- Interfaces and Types: Define message and highlight types consistent with backend schema.
- Integration Points: Connect to backend chat API, PDF viewer, and approval workflow state.
- Side Effects/Dependencies: UI updates for chat disablement and highlight rendering.
- Examples/Conventions: Follow dense, utility-focused, dark mode UI style; use solid buttons for primary actions.
- Testing: Include UI tests for chat flow, highlight rendering, and chat disablement on rejection.

