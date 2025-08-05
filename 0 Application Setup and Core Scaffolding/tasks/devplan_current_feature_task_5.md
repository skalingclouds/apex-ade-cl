# Basic Internal Authentication

Implement basic internal authentication for all backend endpoints.

Goals:
- Restrict access to authenticated users only.
- Block all access if authentication is misconfigured.

Acceptance Criteria:
- All endpoints require authentication (e.g., token or password-based).
- Auth credentials are stored securely (e.g., in environment variables or config file).
- If auth is misconfigured, backend startup fails with a clear error.

Technical Details:
- Architecture/Module Changes: Add an auth module (e.g., auth.py) to handle authentication logic.
- Interfaces and Types: Use FastAPI dependencies for auth enforcement.
- Integration Points: All endpoints must require authentication.
- Side Effects/Dependencies: None.
- Testing: Add tests for successful and failed authentication.

