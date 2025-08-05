# Implement Frontend PDF Upload UI (Drag-and-Drop & File Picker)

Implement the frontend component(s) that allow users to upload PDF files via drag-and-drop and file picker. Ensure the UI provides clear feedback on upload progress, success, and errors, following the utility-focused, dense, dark-mode style guide.

Goals:
- Allow users to select or drag-and-drop PDF files for upload (max 50MB).
- Provide immediate, clear feedback on upload status and errors.

Acceptance Criteria:
- Users can upload PDFs via both drag-and-drop and file picker.
- Upload progress is visually indicated.
- Errors (file too large, wrong type, network issues) are clearly displayed inline.
- UI matches the dense, utility-focused, dark-mode style.

Technical Details:
- Architecture/Module Changes: Add/upload or update a frontend module/component for file uploads.
- Interfaces and Types: Define types for upload status, error messages, and accepted file types (PDF only).
- Integration Points: Connect to the backend upload endpoint (to be implemented in the next step).
- Side Effects/Dependencies: None beyond core frontend frameworks and styling.
- Examples/Conventions: Follow existing frontend patterns and style guide.
- Testing: Include tests for UI feedback, drag-and-drop, file picker, and error handling (mock backend responses).

