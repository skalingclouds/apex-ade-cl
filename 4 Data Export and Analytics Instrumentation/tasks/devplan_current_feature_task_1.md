# Backend: Implement Export Generation and Download Endpoints

Implement backend logic to generate CSV and Markdown exports for each processed document. Expose secure download endpoints for these exports.

Goals:
- Allow users to download extracted data as CSV or Markdown for any document.

Acceptance Criteria:
- For each document, backend can generate and serve CSV and Markdown exports via authenticated endpoints.
- Exports reflect the latest extracted data.
- Endpoints are secure and respect user permissions.
- If export generation fails, return a clear error message.

Technical Details:
- Architecture/Module Changes: Add export generation logic to the document processing or extraction module. Add new endpoints (e.g., /documents/:id/export/csv, /documents/:id/export/markdown).
- Interfaces and Types: Define export request/response types. Ensure document ID and user authentication are required.
- Integration Points: Integrate with the existing document storage and extraction pipeline.
- Database/Schema Changes: No schema changes unless audit logging is required for exports.
- Side Effects/Dependencies: Ensure exports are generated on-demand or cached securely.
- Examples/Conventions: Follow existing API and authentication patterns.
- Testing: Include tests for export generation, endpoint security, and error handling (including retry scenarios).
