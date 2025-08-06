# Backend Enforcement of Workflow Rules and Status Persistence

Ensure backend enforces workflow rules and persists document statuses securely.

Goals:
- Persist document status changes in SQLite with auditability.
- Enforce workflow rules (e.g., chat disabled for rejected docs).
- Ensure compliance with security and privacy requirements.

Acceptance Criteria:
- Status changes are reliably stored and auditable in SQLite.
- Backend prevents chat interactions on rejected documents.
- Data is encrypted at rest and in transit.
- GDPR-compliant deletion is supported.

Technical Details:
- Architecture/Module Changes: Backend logic for status transitions, workflow rule enforcement, and secure storage.
- Interfaces and Types: Status change API, audit log schema.
- Database/Schema Changes: Document table includes status and audit trail.
- Side Effects/Dependencies: Disables chat endpoint for rejected docs.
- Examples/Conventions: Follow backend security and compliance patterns.
- Testing: Include tests for status persistence, rule enforcement, and security edge cases.

