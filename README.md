# Apex ADE - Advanced Document Extraction Platform

Apex ADE (Advanced Document Extraction) is an intelligent document processing platform that leverages the landing.ai SDK for agentic PDF extraction with human-in-the-loop review capabilities.

## Features

- 📄 **PDF Upload & Processing** - Drag-and-drop PDF upload with automatic processing
- 🤖 **Agentic Extraction** - Intelligent data extraction using landing.ai SDK
- 👁️ **Dual-Pane Review** - Side-by-side view of original PDF and extracted content
- ✅ **Approval Workflow** - Approve, reject, or escalate documents
- 💬 **Chat Interface** - Ask questions about documents with contextual highlighting
- 📊 **Data Export** - Export extracted data as CSV or Markdown
- 🌙 **Dark Mode** - Beautiful dark theme optimized for long sessions

## Tech Stack

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + Python + SQLAlchemy
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **PDF Processing**: landing.ai SDK (agentic_doc)

## Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- pip

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/apex-ade-cl.git
cd apex-ade-cl
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

In a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### 4. Access the Application

Open your browser and navigate to `http://localhost:3000`

## Development

### Backend Development

The backend follows a modular structure:

```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core configuration
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   └── services/     # Business logic
├── alembic/          # Database migrations
└── uploads/          # Uploaded PDFs
```

To create a new migration:
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Frontend Development

The frontend uses React with TypeScript:

```
frontend/
├── src/
│   ├── components/   # Reusable components
│   ├── pages/        # Page components
│   ├── services/     # API client
│   ├── utils/        # Utility functions
│   └── styles/       # Global styles
```

## API Documentation

Once the backend is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative API docs: `http://localhost:8000/redoc`

## Docker Deployment

Build and run with Docker:

```bash
docker-compose up --build
```

## Environment Variables

### Backend (.env)

```
APP_NAME=ApexADE
DEBUG=True
DATABASE_URL=sqlite:///./apex_ade.db
SECRET_KEY=your-secret-key-here
MAX_UPLOAD_SIZE=52428800
UPLOAD_DIRECTORY=./uploads
LANDING_AI_API_KEY=your-api-key-if-needed
```

## Project Structure

```
apex-ade-cl/
├── frontend/           # React frontend
├── backend/            # FastAPI backend
├── docs/              # Documentation
├── scripts/           # Utility scripts
├── docker-compose.yml # Docker configuration
└── README.md          # This file
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with the landing.ai SDK for intelligent document processing
- UI inspired by modern dark mode applications
- Icons from Lucide React