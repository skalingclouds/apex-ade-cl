#!/bin/bash

echo "🛑 Stopping Apex ADE Application..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Kill backend processes
echo -e "${BLUE}Stopping backend...${NC}"
pkill -f "uvicorn app.main:app" 2>/dev/null

# Kill frontend processes
echo -e "${BLUE}Stopping frontend...${NC}"
pkill -f "vite.*apex-ade-cl/frontend" 2>/dev/null

# Give processes time to shut down
sleep 2

# Check if any processes are still running
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "⚠️  Backend still running, forcing shutdown..."
    pkill -9 -f "uvicorn app.main:app" 2>/dev/null
fi

if pgrep -f "vite.*apex-ade-cl/frontend" > /dev/null; then
    echo "⚠️  Frontend still running, forcing shutdown..."
    pkill -9 -f "vite.*apex-ade-cl/frontend" 2>/dev/null
fi

echo -e "${GREEN}✅ All services stopped${NC}"