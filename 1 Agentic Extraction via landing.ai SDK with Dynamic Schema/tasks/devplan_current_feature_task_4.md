# Extraction Error Handling and User Feedback

Implement robust error handling for extraction failures, schema mismatches, and SDK errors, providing clear feedback to the user and options to retry or escalate.

Goals:
- Ensure users are informed of errors and can take corrective action.

Acceptance Criteria:
- Extraction errors (SDK/API, schema mismatch, etc.) are logged and surfaced to the user with actionable messages.
- User can retry extraction or escalate the issue.
- Document is marked as failed if unrecoverable.

Technical Details:
- Architecture/Module Changes: Add error handling and escalation logic to backend and frontend.
- Interfaces and Types: Define error response formats and escalation workflow.
- Integration Points: Connect error states to document status and user notification system.
- Side Effects/Dependencies: Ensure errors do not leak sensitive information; comply with privacy/security requirements.
- Examples/Conventions: Use inline feedback and fast transitions per UI style guide.
- Testing: Include tests for all error paths, user feedback, and escalation logic.
