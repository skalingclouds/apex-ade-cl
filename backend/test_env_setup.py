#!/usr/bin/env python3
"""
Test script to verify environment configuration is set up correctly.
Run this after setting up your .env file to verify everything works.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def test_env_setup():
    """Test that environment files are properly configured."""
    
    print(f"{BLUE}{'='*50}{RESET}")
    print(f"{BLUE}ApexADE Environment Configuration Test{RESET}")
    print(f"{BLUE}{'='*50}{RESET}\n")
    
    errors = []
    warnings = []
    
    # Check if we're in the right directory
    if not Path("app").exists():
        print(f"{RED}❌ ERROR: Run this script from the backend directory!{RESET}")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Expected to find: ./app directory")
        return False
    
    # Test 1: Check if .env file exists
    print(f"1. Checking for .env file...")
    if Path(".env").exists():
        print(f"{GREEN}   ✓ .env file exists{RESET}")
        
        # Load the .env file
        load_dotenv(".env")
        
        # Check for Landing.AI key
        landing_key = os.getenv("VISION_AGENT_API_KEY", "")
        if landing_key and landing_key != "your_landing_ai_api_key_here":
            print(f"{GREEN}   ✓ Landing.AI API key configured{RESET}")
        else:
            errors.append("Landing.AI API key not configured in .env")
            print(f"{RED}   ✗ Landing.AI API key not configured{RESET}")
        
        # Check for OpenAI key
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if openai_key and openai_key != "your_openai_api_key_here":
            print(f"{GREEN}   ✓ OpenAI API key configured{RESET}")
        else:
            warnings.append("OpenAI API key not configured (fallback won't work)")
            print(f"{YELLOW}   ⚠ OpenAI API key not configured{RESET}")
    else:
        errors.append(".env file not found - copy .env.example to .env")
        print(f"{RED}   ✗ .env file not found{RESET}")
        print(f"   Run: cp .env.example .env")
    
    print()
    
    # Test 2: Check if .env.landing_ai file exists
    print(f"2. Checking for .env.landing_ai file...")
    if Path(".env.landing_ai").exists():
        print(f"{GREEN}   ✓ .env.landing_ai file exists{RESET}")
        
        # Load and check settings
        load_dotenv(".env.landing_ai")
        batch_size = os.getenv("BATCH_SIZE", "")
        max_workers = os.getenv("MAX_WORKERS", "")
        
        if batch_size == "1":
            print(f"{GREEN}   ✓ BATCH_SIZE=1 (optimized for large docs){RESET}")
        else:
            warnings.append(f"BATCH_SIZE={batch_size} (expected 1)")
        
        if max_workers == "5":
            print(f"{GREEN}   ✓ MAX_WORKERS=5 (optimized for 25 rpm){RESET}")
        else:
            warnings.append(f"MAX_WORKERS={max_workers} (expected 5)")
    else:
        warnings.append(".env.landing_ai not found (using defaults)")
        print(f"{YELLOW}   ⚠ .env.landing_ai file not found{RESET}")
    
    print()
    
    # Test 3: Try importing the config
    print(f"3. Testing configuration import...")
    try:
        from app.core.config import settings
        print(f"{GREEN}   ✓ Configuration loaded successfully{RESET}")
        
        if settings.VISION_AGENT_API_KEY and settings.VISION_AGENT_API_KEY != "your_landing_ai_api_key_here":
            print(f"{GREEN}   ✓ Landing.AI key accessible in config{RESET}")
        else:
            print(f"{RED}   ✗ Landing.AI key not accessible{RESET}")
        
        # Show loaded values (masked)
        if settings.VISION_AGENT_API_KEY:
            masked_key = settings.VISION_AGENT_API_KEY[:10] + "..." if len(settings.VISION_AGENT_API_KEY) > 10 else "***"
            print(f"{BLUE}   → Landing.AI key: {masked_key}{RESET}")
    except ImportError as e:
        errors.append(f"Failed to import config: {e}")
        print(f"{RED}   ✗ Failed to import configuration{RESET}")
    
    print()
    
    # Test 4: Check Landing.AI SDK configuration
    print(f"4. Testing Landing.AI SDK configuration...")
    try:
        from app.core.landing_ai_config import landing_ai_settings
        print(f"{GREEN}   ✓ Landing.AI settings loaded{RESET}")
        print(f"{BLUE}   → Batch size: {landing_ai_settings.batch_size}{RESET}")
        print(f"{BLUE}   → Max workers: {landing_ai_settings.max_workers}{RESET}")
        print(f"{BLUE}   → Max retries: {landing_ai_settings.max_retries}{RESET}")
    except Exception as e:
        warnings.append(f"Landing.AI config not loaded: {e}")
        print(f"{YELLOW}   ⚠ Landing.AI config not loaded (using defaults){RESET}")
    
    print()
    
    # Summary
    print(f"{BLUE}{'='*50}{RESET}")
    print(f"{BLUE}Summary:{RESET}")
    print(f"{BLUE}{'='*50}{RESET}\n")
    
    if not errors and not warnings:
        print(f"{GREEN}✅ All checks passed! Your environment is properly configured.{RESET}")
        print(f"\nYou can now start the server with:")
        print(f"  {BLUE}uvicorn app.main:app --reload{RESET}")
        return True
    else:
        if errors:
            print(f"{RED}Errors found ({len(errors)}):{RESET}")
            for error in errors:
                print(f"  • {error}")
            print()
        
        if warnings:
            print(f"{YELLOW}Warnings ({len(warnings)}):{RESET}")
            for warning in warnings:
                print(f"  • {warning}")
            print()
        
        if errors:
            print(f"{RED}❌ Please fix the errors above before starting the server.{RESET}")
            print(f"\nQuick fix:")
            print(f"  1. Run: {BLUE}./setup_env.sh{RESET}")
            print(f"  2. Enter your API keys when prompted")
            return False
        else:
            print(f"{YELLOW}⚠️  Server will run but with limited functionality.{RESET}")
            return True

if __name__ == "__main__":
    success = test_env_setup()
    sys.exit(0 if success else 1)