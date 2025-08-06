#!/bin/bash

echo "📊 Apex ADE Service Status"
echo "=========================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Check virtual environment
echo -e "\n${BLUE}Python Virtual Environment:${NC}"
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo -e "  ${GREEN}✅ Virtual environment exists${NC}"
    if [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
        PYTHON_VERSION=$("$SCRIPT_DIR/venv/bin/python" --version 2>&1)
        echo -e "  ${GREEN}   Python: $PYTHON_VERSION${NC}"
    fi
else
    echo -e "  ${RED}❌ Virtual environment not found${NC}"
    echo -e "  ${YELLOW}   Run: ./scripts/setup.sh${NC}"
fi

# Check backend dependencies
echo -e "\n${BLUE}Backend Dependencies:${NC}"
if [ -d "$SCRIPT_DIR/venv" ] && [ -f "$SCRIPT_DIR/venv/bin/uvicorn" ]; then
    echo -e "  ${GREEN}✅ Backend dependencies installed${NC}"
else
    echo -e "  ${RED}❌ Backend dependencies not installed${NC}"
    echo -e "  ${YELLOW}   Run: ./scripts/setup.sh${NC}"
fi

# Check frontend dependencies
echo -e "\n${BLUE}Frontend Dependencies:${NC}"
if [ -d "$PROJECT_ROOT/frontend/node_modules" ]; then
    echo -e "  ${GREEN}✅ Node modules installed${NC}"
else
    echo -e "  ${RED}❌ Node modules not found${NC}"
    echo -e "  ${YELLOW}   Run: ./scripts/setup.sh${NC}"
fi

# Check backend service
echo -e "\n${BLUE}Backend Service (port 8000):${NC}"
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Backend is running${NC}"
    echo -e "     http://localhost:8000"
    echo -e "     API Docs: http://localhost:8000/docs"
elif pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo -e "  ${YELLOW}⚠️  Backend process found but port 8000 not listening${NC}"
else
    echo -e "  ${RED}❌ Backend is not running${NC}"
    echo -e "  ${YELLOW}   Run: ./scripts/start-backend.sh${NC}"
fi

# Check frontend service
echo -e "\n${BLUE}Frontend Service (port 3000):${NC}"
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Frontend is running${NC}"
    echo -e "     http://localhost:3000"
elif pgrep -f "vite.*apex-ade-cl/frontend" > /dev/null; then
    echo -e "  ${YELLOW}⚠️  Frontend process found but port 3000 not listening${NC}"
else
    echo -e "  ${RED}❌ Frontend is not running${NC}"
    echo -e "  ${YELLOW}   Run: ./scripts/start-frontend.sh${NC}"
fi

# Check database
echo -e "\n${BLUE}Database:${NC}"
if [ -f "$PROJECT_ROOT/backend/apex_ade.db" ]; then
    DB_SIZE=$(du -h "$PROJECT_ROOT/backend/apex_ade.db" | cut -f1)
    echo -e "  ${GREEN}✅ Database exists (size: $DB_SIZE)${NC}"
else
    echo -e "  ${YELLOW}⚠️  Database not found${NC}"
    echo -e "  ${YELLOW}   Will be created on first run${NC}"
fi

# Check .env file
echo -e "\n${BLUE}Configuration:${NC}"
if [ -f "$PROJECT_ROOT/backend/.env" ]; then
    echo -e "  ${GREEN}✅ Backend .env file exists${NC}"
else
    echo -e "  ${YELLOW}⚠️  Backend .env file not found${NC}"
    if [ -f "$PROJECT_ROOT/backend/.env.example" ]; then
        echo -e "  ${YELLOW}   Run: cp backend/.env.example backend/.env${NC}"
    fi
fi

echo -e "\n=========================="
echo -e "${BLUE}Quick Commands:${NC}"
echo -e "  Setup:     ${GREEN}./scripts/setup.sh${NC}"
echo -e "  Start all: ${GREEN}./scripts/start-all.sh${NC}"
echo -e "  Stop all:  ${GREEN}./scripts/stop-all.sh${NC}"
echo -e "  Status:    ${GREEN}./scripts/status.sh${NC}"