#!/bin/bash

echo "🚀 Setting up NativeADE..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met!${NC}"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Backend setup
echo -e "\n${BLUE}Setting up backend...${NC}"
cd "$PROJECT_ROOT/backend"

# Create virtual environment in scripts directory
echo "Creating Python virtual environment..."
python3 -m venv "$SCRIPT_DIR/venv"
source "$SCRIPT_DIR/venv/bin/activate"

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Setup environment
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env file. Please edit it with your settings.${NC}"
fi

# Run migrations
echo "Running database migrations..."
alembic upgrade head

echo -e "${GREEN}✅ Backend setup complete!${NC}"

# Frontend setup
echo -e "\n${BLUE}Setting up frontend...${NC}"
cd "$PROJECT_ROOT/frontend"

# Install dependencies
echo "Installing Node dependencies..."
npm install

echo -e "${GREEN}✅ Frontend setup complete!${NC}"

# Final instructions
echo -e "\n${GREEN}🎉 Setup complete!${NC}"
echo -e "\nTo start the application:"
echo -e "${BLUE}1. Start the backend:${NC}"
echo "   ./scripts/start-backend.sh"
echo -e "\n${BLUE}2. Start the frontend (in a new terminal):${NC}"
echo "   ./scripts/start-frontend.sh"
echo -e "\n${BLUE}3. Open your browser:${NC}"
echo "   http://localhost:3000"
echo -e "\n${GREEN}Happy coding! 🚀${NC}"