# Environment Configuration Setup

## You Need TWO .env Files

### 1. Main `.env` File (Required)
**Location:** `/backend/.env`

This file contains your API keys and main configuration:

```bash
# Landing.AI API Key (REQUIRED)
VISION_AGENT_API_KEY=your_landing_ai_api_key_here

# OpenAI API Key (REQUIRED for fallback)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Override OpenAI model
OPENAI_MODEL=gpt-4-turbo-preview

# Database (default is fine)
DATABASE_URL=sqlite:///./apex_ade.db

# File upload settings
MAX_UPLOAD_SIZE=524288000  # 500MB for large documents
UPLOAD_DIRECTORY=./uploads
```

### 2. Landing.AI Settings `.env.landing_ai` (Optional but Recommended)
**Location:** `/backend/.env.landing_ai`

This file optimizes Landing.AI SDK behavior (NO API keys here):

```bash
# Number of documents to process in parallel
BATCH_SIZE=1

# Number of chunks to process in parallel per document
MAX_WORKERS=5

# Retry configuration
MAX_RETRIES=50
MAX_RETRY_WAIT_TIME=30

# Logging style (inline_block shows progress blocks)
RETRY_LOGGING_STYLE=inline_block
```

## How It Works

1. **`app/core/config.py`** loads from `.env` to get:
   - `VISION_AGENT_API_KEY` (your Landing.AI key)
   - `OPENAI_API_KEY` (your OpenAI key)
   - Other app settings

2. **`app/core/landing_ai_config.py`** loads from `.env.landing_ai` to get:
   - `BATCH_SIZE`, `MAX_WORKERS`, etc.
   - These override Landing.AI SDK defaults
   - NO API keys needed here

## Quick Setup

1. Create the main `.env` file:
```bash
cd backend
cp .env.example .env  # If you have an example
# Or create new:
cat > .env << 'EOF'
VISION_AGENT_API_KEY=your_landing_ai_key_here
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=sqlite:///./apex_ade.db
MAX_UPLOAD_SIZE=524288000
UPLOAD_DIRECTORY=./uploads
EOF
```

2. The `.env.landing_ai` file is already created with optimal settings

3. Start the server:
```bash
uvicorn app.main:app --reload
```

## Important Notes

- **Never commit `.env` files** to git (they contain secrets)
- The `.env.landing_ai` can be committed (no secrets, just settings)
- Both files are automatically loaded when the app starts
- Landing.AI SDK reads both environment variables AND its config file

## Verify Configuration

When the server starts, you should see:
```
INFO: Settings loaded: {
  "batch_size": 1,        # From .env.landing_ai
  "max_workers": 5,       # From .env.landing_ai
  "vision_agent_api_key": "xxx..."  # From .env
}
```

If you see `batch_size: 4` (default), the `.env.landing_ai` file isn't being loaded.