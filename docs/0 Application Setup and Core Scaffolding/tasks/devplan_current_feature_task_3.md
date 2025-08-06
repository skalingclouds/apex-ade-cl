# SQLite Database Schema and Initialization

Implement SQLite database initialization and schema for documents and chat logs.

Goals:
- Persist uploaded PDFs, extracted data, and chat logs securely.
- Ensure database is initialized on backend startup.

Acceptance Criteria:
- SQLite database is created on backend startup if not present.
- Tables:
  - documents (id, filename, upload_time, status, extracted_data_path, user_id, etc.)
  - chat_logs (id, document_id, user_id, message, response, timestamp)
- Clear error logging and graceful shutdown if DB initialization fails.

Technical Details:
- Architecture/Module Changes: Add a database module (e.g., db.py) to handle connections and migrations.
- Interfaces and Types: Use SQLAlchemy or similar ORM for models (examples only).
- Integration Points: Backend endpoints should be able to access the DB module.
- Database/Schema Changes: As described above.
- Side Effects/Dependencies: None.
- Testing: Add a test to verify tables are created and basic CRUD works.

