# Apex ADE Scripts

This directory contains utility scripts for managing the Apex ADE application.

## Scripts Overview

### setup.sh
Initial setup script that:
- Checks prerequisites (Python 3, Node.js, npm)
- Creates Python virtual environment in `scripts/venv`
- Installs backend Python dependencies
- Runs database migrations
- Installs frontend Node dependencies
- Creates `.env` file from example if needed

### start-backend.sh
Starts the backend FastAPI server:
- Activates virtual environment from `scripts/venv`
- Runs on http://localhost:8000
- API documentation available at http://localhost:8000/docs
- Includes hot-reload for development

### start-frontend.sh
Starts the frontend React development server:
- Runs on http://localhost:3000
- Includes hot-reload for development

### start-all.sh
Convenience script to start both backend and frontend:
- Runs setup automatically if venv is missing
- Starts both services in background
- Graceful shutdown on Ctrl+C

### stop-all.sh
Stops all running services:
- Gracefully terminates backend and frontend processes
- Forces shutdown if processes don't respond

### status.sh
Comprehensive status check that shows:
- Virtual environment status
- Dependency installation status
- Service running status (backend/frontend)
- Database existence
- Configuration file status
- Helpful next steps for any issues

## Quick Start

```bash
# First time setup
./scripts/setup.sh

# Start everything
./scripts/start-all.sh

# Check status
./scripts/status.sh

# Stop everything
./scripts/stop-all.sh
```

## Directory Structure

```
scripts/
├── venv/           # Python virtual environment (created by setup.sh)
├── setup.sh        # Initial setup script
├── start-backend.sh    # Start backend server
├── start-frontend.sh   # Start frontend server
├── start-all.sh    # Start all services
├── stop-all.sh     # Stop all services
└── status.sh       # Check system status
```

## Notes

- Virtual environment is stored in `scripts/venv` for centralized management
- All scripts use relative paths and auto-detect project root
- Scripts include error checking and helpful error messages
- Backend runs on port 8000, frontend on port 3000