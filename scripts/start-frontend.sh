#!/bin/bash

echo "Starting Apex ADE Frontend..."

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Navigate to frontend directory
cd "$PROJECT_ROOT/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Node modules not found. Please run ./scripts/setup.sh first."
    exit 1
fi

echo "Running on http://localhost:3000"
echo "Press Ctrl+C to stop"

npm run dev