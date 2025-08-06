#!/usr/bin/env python3
"""Test script to verify API key configuration is working correctly."""

import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_api_key_configuration():
    """Test that the API key is properly configured and accessible."""
    
    print("Testing API key configuration...")
    print("=" * 50)
    
    # First check if .env file exists
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        print(f"✓ .env file found at: {env_path}")
        
        # Read .env file to check key name
        with open(env_path, 'r') as f:
            env_content = f.read()
            if 'VISION_AGENT_API_KEY' in env_content:
                print("✓ VISION_AGENT_API_KEY found in .env file")
            elif 'LANDING_AI_API_KEY' in env_content:
                print("⚠️  Found LANDING_AI_API_KEY in .env - please rename to VISION_AGENT_API_KEY")
            else:
                print("❌ No API key found in .env file")
    else:
        print(f"❌ .env file not found at: {env_path}")
        print("   Please create a .env file with: VISION_AGENT_API_KEY=your-api-key-here")
        return False
    
    print("\n" + "=" * 50)
    print("Testing settings import...")
    
    try:
        from app.core.config import settings
        
        # Check if the API key is loaded
        if hasattr(settings, 'VISION_AGENT_API_KEY'):
            if settings.VISION_AGENT_API_KEY:
                print(f"✓ VISION_AGENT_API_KEY loaded from settings: {settings.VISION_AGENT_API_KEY[:10]}...")
            else:
                print("❌ VISION_AGENT_API_KEY is empty in settings")
                return False
        else:
            print("❌ VISION_AGENT_API_KEY not found in settings")
            return False
            
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("Testing LandingAIService initialization...")
    
    try:
        from app.services.landing_ai_service import LandingAIService
        
        # Initialize the service
        service = LandingAIService()
        
        # Check if environment variable was set
        env_key = os.environ.get('VISION_AGENT_API_KEY')
        if env_key:
            print(f"✓ Environment variable set: VISION_AGENT_API_KEY={env_key[:10]}...")
            
            # Verify it matches the settings
            if env_key == settings.VISION_AGENT_API_KEY:
                print("✓ Environment variable matches settings")
            else:
                print("⚠️  Environment variable doesn't match settings")
        else:
            print("❌ VISION_AGENT_API_KEY not set in environment")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing LandingAIService: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All checks passed! API key configuration is correct.")
    print("\nNext steps:")
    print("1. Make sure your .env file contains: VISION_AGENT_API_KEY=your-actual-api-key")
    print("2. Restart the backend server: pkill -9 -f uvicorn && cd backend && uvicorn app.main:app --reload")
    print("3. The API key will be automatically available to the Landing.AI SDK")
    
    return True

if __name__ == "__main__":
    success = test_api_key_configuration()
    sys.exit(0 if success else 1)