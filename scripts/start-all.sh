#!/bin/bash

echo "🚀 Starting Apex ADE Application..."

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if venv exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Running setup...${NC}"
    "$SCRIPT_DIR/setup.sh"
    if [ $? -ne 0 ]; then
        echo "❌ Setup failed. Please check the error messages above."
        exit 1
    fi
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down...${NC}"
    # Kill all child processes
    jobs -p | xargs -r kill 2>/dev/null
    wait
    echo -e "${GREEN}✅ Application stopped${NC}"
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Start backend in background
echo -e "${BLUE}Starting backend server...${NC}"
"$SCRIPT_DIR/start-backend.sh" &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start. Check the logs above."
    exit 1
fi

# Start frontend in background
echo -e "${BLUE}Starting frontend server...${NC}"
"$SCRIPT_DIR/start-frontend.sh" &
FRONTEND_PID=$!

# Wait a bit for frontend to start
sleep 3

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Frontend failed to start. Check the logs above."
    exit 1
fi

echo -e "\n${GREEN}✅ Application is running!${NC}"
echo -e "${BLUE}Backend:${NC} http://localhost:8000"
echo -e "${BLUE}API Docs:${NC} http://localhost:8000/docs"
echo -e "${BLUE}Frontend:${NC} http://localhost:3000"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}\n"

# Wait for all background processes
wait