<!-- feature_id: cmdwfkc5f00qj4ny8fucxgv0g -->

Implement the feature: Application Setup and Core Scaffolding

This feature is part of the following context from the PRD:  
The application is an internal business tool for agentic PDF extraction and review, targeting business analysts and data processors. It requires a robust, secure, and modular architecture to support PDF upload, agentic extraction (via landing.ai SDK), dual-pane human-in-the-loop review, chat-based document interaction, approval workflows, and secure data storage. The system must be easy to develop, test, and deploy, with clear separation of concerns and support for future extensibility.

Feature Goals:
- Establish a monorepo with clear separation between frontend (React) and backend (FastAPI) codebases.
- Provide a FastAPI backend with stubbed REST endpoints for all major flows (upload, parse, extract, review, chat, approval, export).
- Bootstrap a React frontend with routing, state management, and a basic layout for dual-pane review and chat.
- Initialize a SQLite database with tables for documents and chat logs.
- Set up local file storage for PDFs and extracted data.
- Implement basic internal authentication (token or password-based) for all backend endpoints.

Feature Acceptance Criteria:
- Monorepo structure exists with distinct frontend and backend directories.
- FastAPI backend runs and exposes all required endpoints as stubs (returning placeholder responses).
- React frontend runs, supports navigation/routing, and displays a basic dual-pane review and chat layout.
- SQLite database is created and includes `documents` and `chat_logs` tables as per schema.
- Uploaded files are stored in a local, configurable directory; extracted data directory exists.
- Authentication is required for all backend endpoints; misconfiguration blocks access.
- Application fails gracefully with clear error messages if DB or storage paths are misconfigured.

Technical Details:

- Architecture/Module Changes:
    - Create a monorepo with at least two top-level directories: `/frontend` (React app) and `/backend` (FastAPI app).
    - Backend should be modular, separating API routes, database models, authentication, and file storage logic.
    - Frontend should use a component-based structure, with routing and state management (e.g., React Router, Context API or Redux).

- Interfaces and Types:
    - Backend: Define Pydantic models for document metadata and chat logs (matching the provided schema).
    - Frontend: Define TypeScript interfaces or PropTypes for document, extraction, and chat data structures.

- Integration Points:
    - Backend REST API endpoints (stubbed) for:
        - `POST /api/upload`
        - `GET /api/documents/{id}`
        - `GET /api/documents/{id}/pdf`
        - `GET /api/documents/{id}/markdown`
        - `POST /api/documents/{id}/parse`
        - `POST /api/documents/{id}/extract`
        - `POST /api/documents/{id}/approve`
        - `POST /api/documents/{id}/reject`
        - `POST /api/documents/{id}/escalate`
        - `POST /api/documents/{id}/chat`
        - `GET /api/documents/{id}/export/csv`
        - `GET /api/documents/{id}/export/md`
    - All endpoints should require authentication (token/password in header or session).
    - File uploads should be stored in a local directory (e.g., `/data/pdfs`), with extracted data in `/data/extracted`.

- Database/Schema Changes:
    - Initialize SQLite database with:
        - `documents` table:
            - `id` INTEGER PRIMARY KEY
            - `filename` TEXT
            - `filepath` TEXT
            - `status` TEXT
            - `extracted_md` TEXT
            - `uploaded_at` TIMESTAMP
            - `processed_at` TIMESTAMP
        - `chat_logs` table:
            - `id` INTEGER PRIMARY KEY
            - `document_id` INTEGER (foreign key)
            - `query` TEXT
            - `response` TEXT
            - `created_at` TIMESTAMP

- Side Effects/Dependencies:
    - On backend startup, check for existence and writability of file storage directories; fail with clear error if not present.
    - On DB initialization failure, log error and halt startup.
    - Authentication misconfiguration (e.g., missing secret/token) should block all access and log a clear error.
    - Frontend should provide a basic login form if authentication is required.

- Examples/Conventions:
    - Follow idiomatic FastAPI and React project structures.
    - Use environment variables or config files for secrets, DB path, and storage directories.
    - Use async endpoints in FastAPI where appropriate.
    - Use React functional components and hooks.
    - Use dark mode and dense layout as per style guide.

- Testing:
    - Backend: Include basic tests for endpoint authentication, DB initialization, and file storage checks.
    - Frontend: Include smoke tests for routing and layout rendering.
    - Test error handling for DB/storage/auth misconfiguration as described in edge cases.

- Other Areas:
    - Ensure all code is ready for future extension (e.g., real extraction logic, chat integration).
    - Document setup steps and configuration in a top-level README.
    - Do not implement actual extraction, parsing, or chat logic—only stubs/placeholders.

This scaffolding will provide a robust foundation for rapid development and iteration of the agentic PDF extraction tool, ensuring all core architectural requirements and constraints are met from the outset.