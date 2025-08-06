#!/bin/bash

echo "Starting Apex ADE Backend..."

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Navigate to backend directory
cd "$PROJECT_ROOT/backend"

# Check if venv exists in scripts directory
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "❌ Virtual environment not found. Please run ./scripts/setup.sh first."
    exit 1
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

echo "Running on http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
echo "Press Ctrl+C to stop"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000