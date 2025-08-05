#!/bin/bash

echo "Starting NativeADE Backend..."

cd /Users/chris/ai/naitiveade/.conductor/valletta/nativeade/backend
source venv/bin/activate

echo "Running on http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
echo "Press Ctrl+C to stop"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000