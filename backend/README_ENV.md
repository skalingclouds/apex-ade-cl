# Environment Configuration - Quick Answer

## You were confused about: "there's no key in there, so now I'm confused what is your code looking for name wise .env? both?"

### YES, THE CODE USES BOTH FILES:

1. **`.env`** - Contains your SECRET API KEYS
   - `VISION_AGENT_API_KEY` = Your Landing.AI key
   - `OPENAI_API_KEY` = Your OpenAI key
   - This file is loaded by `app/core/config.py`

2. **`.env.landing_ai`** - Contains SDK SETTINGS (no keys!)
   - `MAX_WORKERS=5` - How many chunks to process in parallel
   - `BATCH_SIZE=1` - How many documents at once
   - This file is loaded by Landing.AI SDK automatically

## Quick Setup (30 seconds)

### Option 1: Use the setup script
```bash
cd backend
./setup_env.sh
# Enter your Landing.AI key when prompted
# Enter your OpenAI key when prompted
```

### Option 2: Manual setup
```bash
cd backend
cp .env.example .env
# Edit .env and replace:
#   your_landing_ai_api_key_here → your actual Landing.AI key
#   your_openai_api_key_here → your actual OpenAI key
```

## Why Two Files?

- **`.env`** = Your secrets (API keys, passwords)
  - Never commit this to git!
  - Contains sensitive information
  
- **`.env.landing_ai`** = Performance settings
  - Safe to commit to git (no secrets)
  - Optimizes how fast documents are processed
  - Already configured optimally for your paid plan (25 rpm)

## Verify It's Working

Start the server:
```bash
uvicorn app.main:app --reload
```

You should see in the logs:
```
INFO: Settings loaded: {
  "batch_size": 1,        # From .env.landing_ai ✓
  "max_workers": 5,       # From .env.landing_ai ✓
  "vision_agent_api_key": "sk-..."  # From .env ✓
}
```

If you see `batch_size: 4` (the default), then `.env.landing_ai` isn't being loaded.

## Common Issues

### "API key not found"
- You forgot to copy `.env.example` to `.env`
- Or you didn't replace the placeholder text with your actual keys

### "Rate limit exceeded"
- Your `.env.landing_ai` isn't being loaded
- Check that the file exists in the backend directory

### "ImportError"
- Make sure both files are in the `/backend` directory, not `/backend/app`

## File Locations

```
backend/
├── .env                 ← Your API keys go here
├── .env.landing_ai      ← SDK settings (already configured)
├── .env.example         ← Template to copy from
├── ENV_SETUP.md         ← Detailed documentation
└── README_ENV.md        ← This file (quick reference)
```

## TL;DR

1. Copy `.env.example` to `.env`
2. Add your API keys to `.env`
3. Leave `.env.landing_ai` as-is (it's already optimized)
4. Start the server with `uvicorn app.main:app --reload`

That's it! The app loads both files automatically.