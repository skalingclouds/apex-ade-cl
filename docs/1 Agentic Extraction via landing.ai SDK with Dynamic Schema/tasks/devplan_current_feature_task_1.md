# Integrate Backend with landing.ai SDK for PDF Parsing

Implement backend logic to receive an uploaded PDF (from the ingestion workflow), call the landing.ai SDK's parse endpoint, and return the detected fields to the frontend.

Goals:
- Enable backend to process PDFs using landing.ai SDK and expose detected fields to frontend.

Acceptance Criteria:
- Backend endpoint accepts PDF reference or file.
- Calls landing.ai SDK parse endpoint.
- Returns detected fields (field names/types/positions) to frontend in a structured format.
- Handles SDK/API errors and returns appropriate error messages.

Technical Details:
- Architecture/Module Changes: Add a backend service/module for landing.ai integration.
- Interfaces and Types: Define response schema for detected fields (example: list of {name, type, position}).
- Integration Points: Connect to existing PDF ingestion/upload workflow; expose new API endpoint for field detection.
- Side Effects/Dependencies: Requires landing.ai SDK/API credentials/configuration.
- Examples/Conventions: Follow existing backend API and error handling conventions.
- Testing: Include tests for successful parse, SDK errors, and malformed PDFs.
