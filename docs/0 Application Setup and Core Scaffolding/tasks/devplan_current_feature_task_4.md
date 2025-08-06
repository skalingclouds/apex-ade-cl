# Local File Storage Setup

Implement local file storage for uploaded PDFs and extracted data.

Goals:
- Store PDFs and extracted data securely and reliably on the server.
- Ensure storage paths are configurable and checked on startup.

Acceptance Criteria:
- PDFs are saved to a dedicated directory (e.g., /data/pdfs).
- Extracted data (e.g., Markdown) is saved to a separate directory (e.g., /data/extracted).
- On backend startup, verify storage paths exist and are writable; fail gracefully with actionable error if not.

Technical Details:
- Architecture/Module Changes: Add a storage module to handle file operations.
- Interfaces and Types: Define helper functions for saving/retrieving files.
- Integration Points: Backend endpoints (upload, extract, export) should use the storage module.
- Side Effects/Dependencies: Directory creation, permissions checks.
- Testing: Add a test to verify files can be saved and read.

