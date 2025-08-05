# Backend: Analytics Event Logging

Implement analytics event logging for uploads, approvals, rejections, and chat interactions. Ensure logging is robust and non-blocking for user actions.

Goals:
- Track core user actions for analytics and reporting.
- Ensure analytics failures do not impact user experience.

Acceptance Criteria:
- Events are logged for: PDF upload, document approval, rejection, escalation, and chat interactions.
- If logging fails, error is recorded but user action proceeds.
- Events are timestamped and associated with user and document IDs.

Technical Details:
- Architecture/Module Changes: Add analytics logging module or service.
- Interfaces and Types: Define event types and payload schemas.
- Integration Points: Hook into existing workflow endpoints (upload, approval, chat, etc.).
- Database/Schema Changes: Add analytics event table/collection if not present.
- Side Effects/Dependencies: Ensure logging is asynchronous and resilient.
- Examples/Conventions: Follow existing logging and error handling conventions.
- Testing: Add tests for event logging, error handling, and data integrity.
