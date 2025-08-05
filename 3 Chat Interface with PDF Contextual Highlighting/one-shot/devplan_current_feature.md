<!-- feature_id: cmdwfkc6700qr4ny8wu7pkgjv -->

Implement the feature: Chat Interface with PDF Contextual Highlighting

This feature is part of the following context from the PRD:
The system is an internal business tool for agentic PDF data extraction and review. Users upload PDFs, which are processed using the landing.ai SDK, and review extracted data in a dual-pane interface (PDF + Markdown). The chat interface allows users to interact with an AI agent to ask questions about the document, with the agent referencing and highlighting relevant sections in the original PDF. Chat logs are stored for each document, and chat is disabled if a document is rejected. Security, GDPR compliance, and robust error handling are required.

Feature Goals:
- Enable users to ask questions about a PDF via a chat interface.
- AI agent responds with contextually relevant answers, referencing and highlighting the appropriate section(s) in the PDF.
- Display chat history per document, persistently stored.
- Disable chat for rejected documents.
- Handle edge cases gracefully (e.g., missing highlights, storage failures).

Feature Acceptance Criteria:
1. Users can send chat queries and view AI responses in the frontend chat component.
2. Backend processes queries, references extracted data and PDF content, and returns responses with highlight metadata (e.g., page number, bounding box).
3. PDF viewer highlights referenced sections based on AI response metadata.
4. All chat logs are stored in the `chat_logs` SQLite table and associated with the document.
5. Chat interface is disabled for documents with status "rejected".
6. If AI cannot find an answer, a fallback response is returned and user is prompted for clarification.
7. If highlight mapping fails, response is shown without highlight and the issue is logged.
8. If chat log storage fails, user is notified and the system retries once before erroring.

Technical Details:

- Architecture/Module Changes:
  - **Backend (FastAPI):**
    - Implement `/api/documents/{id}/chat` POST endpoint to accept chat queries, process them, and return responses with highlight metadata.
    - Integrate with landing.ai SDK and/or internal logic to reference extracted data and PDF content.
    - Generate highlight metadata (e.g., page number, bounding box coordinates) for referenced PDF sections.
    - Store chat logs in the `chat_logs` table, associating each entry with the document.
    - Implement logic to disable chat for rejected documents (status check).
    - Implement error handling for highlight mapping and chat log storage as described.
  - **Frontend (React):**
    - Add chat component to the review interface, allowing users to send queries and display AI responses.
    - Display chat history for the current document.
    - Integrate with PDF viewer (PDF.js or wrapper) to highlight referenced sections based on metadata from backend.
    - Disable chat input and display appropriate message if document is rejected.
    - Handle fallback responses and highlight mapping failures gracefully in the UI.

- Interfaces and Types:
  - **Chat API Request:** `{ "query": string }`
  - **Chat API Response:** `{ "response": string, "highlight": { "page": int, "bbox": [float, float, float, float] } | null }`
  - **Chat Log DB Schema:** As specified in the tech brief (`chat_logs` table: id, document_id, query, response, created_at).
  - **Highlight Metadata:** Example: `{ "page": 2, "bbox": [x0, y0, x1, y1] }` (coordinates in PDF units).

- Integration Points:
  - **Backend:** Integrate with landing.ai SDK for document context and extraction data; use internal logic or SDK features to map answers to PDF locations.
  - **Frontend:** Integrate chat component with REST API; integrate PDF viewer with highlight overlay functionality.
  - **Database:** Store and retrieve chat logs per document; ensure chat logs are linked to document IDs.

- Database/Schema Changes:
  - Use the `chat_logs` table as defined in the tech brief; no additional schema changes required.

- Side Effects/Dependencies:
  - Requires dual-pane review and approval workflow to be in place.
  - PDF viewer must support highlight overlays based on backend-provided metadata.
  - Chat is disabled if document status is "rejected".

- Examples/Conventions:
  - Follow existing REST API conventions and error handling patterns.
  - Use React component conventions for UI; use PDF.js or approved wrapper for PDF rendering and highlighting.
  - Use Pydantic models for API request/response validation in FastAPI.

- Testing:
  - Include backend tests for chat endpoint: normal queries, fallback responses, highlight mapping failures, chat log storage failures.
  - Include frontend tests for chat UI: sending/receiving messages, displaying highlights, disabling chat for rejected documents, handling fallback and error states.
  - Test edge cases as described in the PRD and tech brief.

- Security & Compliance:
  - Ensure all chat data is encrypted at rest and in transit.
  - Sanitize user input to prevent injection attacks.
  - Ensure GDPR compliance for chat logs (deletion on request).

- Analytics:
  - Ensure chat interactions are tracked per document for analytics as described in the PRD.

Implement this feature in alignment with the above requirements, integrating with existing modules and following the project's architectural and coding conventions.