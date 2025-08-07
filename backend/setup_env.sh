#!/bin/bash

# Setup script for ApexADE environment configuration
# This script helps you create the required .env file with your API keys

echo "========================================="
echo "ApexADE Environment Configuration Setup"
echo "========================================="
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  WARNING: .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled. Existing .env file preserved."
        exit 0
    fi
fi

# Check if .env.example exists
if [ ! -f ".env.example" ]; then
    echo "❌ ERROR: .env.example file not found!"
    echo "Please ensure you're running this from the backend directory."
    exit 1
fi

# Copy .env.example to .env
cp .env.example .env
echo "✅ Created .env file from template"
echo ""

# Prompt for API keys
echo "Please enter your API keys (they will be saved to .env):"
echo ""

# Landing.AI API Key
read -p "Landing.AI API Key (from https://landing.ai/dashboard): " landing_key
if [ ! -z "$landing_key" ]; then
    # Use sed to replace the placeholder
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/VISION_AGENT_API_KEY=your_landing_ai_api_key_here/VISION_AGENT_API_KEY=$landing_key/" .env
    else
        # Linux
        sed -i "s/VISION_AGENT_API_KEY=your_landing_ai_api_key_here/VISION_AGENT_API_KEY=$landing_key/" .env
    fi
    echo "✅ Landing.AI API Key configured"
else
    echo "⚠️  WARNING: No Landing.AI API Key provided - you'll need to add it manually"
fi

echo ""

# OpenAI API Key
read -p "OpenAI API Key (from https://platform.openai.com/api-keys): " openai_key
if [ ! -z "$openai_key" ]; then
    # Use sed to replace the placeholder
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/OPENAI_API_KEY=your_openai_api_key_here/OPENAI_API_KEY=$openai_key/" .env
    else
        # Linux
        sed -i "s/OPENAI_API_KEY=your_openai_api_key_here/OPENAI_API_KEY=$openai_key/" .env
    fi
    echo "✅ OpenAI API Key configured"
else
    echo "⚠️  WARNING: No OpenAI API Key provided - you'll need to add it manually"
fi

echo ""
echo "========================================="
echo "Configuration Summary:"
echo "========================================="
echo ""
echo "✅ Main configuration file: .env (contains your API keys)"
echo "✅ SDK settings file: .env.landing_ai (already optimized)"
echo ""
echo "Files created/updated:"
echo "  - .env (with your API keys)"
echo "  - .env.landing_ai (already exists with optimal settings)"
echo ""
echo "To start the server, run:"
echo "  uvicorn app.main:app --reload"
echo ""
echo "To verify your configuration:"
echo "  1. Start the server"
echo "  2. Check the logs for 'Settings loaded' message"
echo "  3. You should see batch_size=1 and max_workers=5"
echo ""
echo "⚠️  IMPORTANT: Never commit .env to git (it contains secrets!)"
echo ""
echo "Setup complete! 🎉"