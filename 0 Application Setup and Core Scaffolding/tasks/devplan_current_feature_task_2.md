# FastAPI Backend Scaffolding with Endpoint Stubs

Set up the FastAPI backend with stubbed endpoints for all major flows.

Goals:
- Provide a REST API skeleton for all required flows: upload, parse, extract, review, chat, approval, export.
- Ensure backend is ready for further feature development.

Acceptance Criteria:
- FastAPI app is initialized in `/backend`.
- Endpoints exist for:
  - POST /upload
  - POST /parse
  - POST /extract
  - GET /review/{document_id}
  - POST /chat/{document_id}
  - POST /approval/{document_id}
  - GET /export/{document_id}
- Each endpoint returns a stubbed JSON response.
- API gateway (if needed) is documented or stubbed.

Technical Details:
- Architecture/Module Changes: Organize endpoints in logical modules (e.g., routes/upload.py, routes/chat.py).
- Interfaces and Types: Use Pydantic models for request/response schemas (examples only).
- Integration Points: None yet, but endpoints should be ready for frontend consumption.
- Testing: Add a basic test to ensure all endpoints return 200 OK.
- Side Effects/Dependencies: None at this step.

