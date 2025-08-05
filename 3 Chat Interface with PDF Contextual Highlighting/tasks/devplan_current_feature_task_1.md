# Implement Backend Chat Processing API with Highlight Metadata

Implement the backend API endpoint that receives chat queries, processes them using the AI agent (leveraging the landing.ai SDK and/or API), and returns structured responses including answer text and highlight metadata referencing the original PDF.

Goals:
- Enable chat-based queries about the PDF and extracted data.
- Return AI responses with metadata for highlighting relevant PDF sections.
- Handle cases where the AI cannot find an answer or highlight mapping fails.

Acceptance Criteria:
- API accepts chat queries with document context (document ID or similar).
- AI responses include: answer text, highlight metadata (e.g., page number, bounding box coordinates), and a fallback message if no answer is found.
- If highlight mapping fails, response is returned without highlight and the issue is logged.
- API returns appropriate error codes/messages for failures.

Technical Details:
- Architecture/Module Changes: Add a chat processing module/service to the backend. Integrate with the landing.ai SDK/API for document Q&A and highlight extraction.
- Interfaces and Types: Define response schema: { answer: string, highlights?: Array<{ page: number, bbox: [x1, y1, x2, y2] }>, fallback?: boolean }
- Integration Points: Connect to document storage (for PDF/extracted data), and approval workflow (to check document status).
- Database/Schema Changes: Ensure chat logs can be stored in SQLite, associated with document IDs.
- Side Effects/Dependencies: Log highlight mapping failures for monitoring.
- Examples/Conventions: Follow existing API and error handling conventions.
- Testing: Include tests for successful Q&A, fallback responses, highlight mapping failures, and error handling.

