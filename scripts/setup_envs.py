#!/usr/bin/env python3
"""
Interactive environment setup script for Apex ADE.
Creates/updates backend/.env and frontend/.env files with user input.
"""
import os
import re
import sys
import json
import getpass
from datetime import datetime
from pathlib import Path


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def mask_input(prompt):
    """Get user input without echoing to screen."""
    return getpass.getpass(prompt)


def get_input(prompt, default=None, choices=None, is_secret=False, validator=None):
    """
    Get user input with validation and defaults.
    
    Args:
        prompt: The prompt to display
        default: Default value if user presses Enter
        choices: List of valid choices
        is_secret: Whether to mask input (for passwords/keys)
        validator: Function to validate input
        
    Returns:
        User input or default value
    """
    display_prompt = f"{prompt} [{default}]: " if default is not None else f"{prompt}: "
    
    if choices:
        display_prompt = f"{prompt} {choices} [{default}]: "
    
    while True:
        if is_secret:
            value = mask_input(display_prompt)
        else:
            value = input(display_prompt)
        
        # Use default if empty
        if not value and default is not None:
            return default
        
        # Validate choices
        if choices and value not in choices:
            print(f"Error: Please enter one of {choices}")
            continue
            
        # Custom validation
        if validator and value:
            try:
                value = validator(value)
                return value
            except ValueError as e:
                print(f"Error: {e}")
                continue
                
        if value or default is None:
            return value


def validate_int(value):
    """Validate and convert to integer."""
    try:
        result = int(value)
        if result < 0:
            raise ValueError("Value must be a positive integer")
        return result
    except ValueError:
        raise ValueError("Please enter a valid integer")


def validate_url(value):
    """Simple URL validation."""
    if not value.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")
    return value


def parse_env_file(file_path):
    """Parse existing .env file into a dictionary."""
    env_vars = {}
    
    if not os.path.exists(file_path):
        return env_vars
        
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip('"\'')
                
    return env_vars


def write_env_file(file_path, env_vars, header=None):
    """Write environment variables to file."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w') as f:
        if header:
            f.write(f"# {header}\n")
            f.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
        # Write variables sorted by key
        for key in sorted(env_vars.keys()):
            value = env_vars[key]
            # Quote values with spaces
            if ' ' in str(value):
                f.write(f'{key}="{value}"\n')
            else:
                f.write(f'{key}={value}\n')


def setup_backend_env():
    """Interactive setup for backend/.env file."""
    print("\n=== Backend Environment Setup ===\n")
    
    # Load existing values if any
    backend_env_path = 'backend/.env'
    existing_vars = parse_env_file(backend_env_path)
    
    # App settings
    app_name = get_input("App name", default=existing_vars.get('APP_NAME', 'ApexADE'))
    app_version = get_input("App version", default=existing_vars.get('APP_VERSION', '0.1.0'))
    api_v1_str = get_input("API version path", default=existing_vars.get('API_V1_STR', '/api/v1'))
    
    # Database settings
    database_url = get_input("Database URL", default=existing_vars.get('DATABASE_URL', 'sqlite:///./apex_ade.db'))
    
    # Upload settings
    upload_dir = get_input("Upload directory", default=existing_vars.get('UPLOAD_DIRECTORY', './uploads'))
    max_upload_size = get_input(
        "Maximum upload size (bytes)", 
        default=existing_vars.get('MAX_UPLOAD_SIZE', '1073741824'),
        validator=validate_int
    )
    
    # CORS settings
    cors_origins = get_input(
        "CORS origins (comma-separated)",
        default=existing_vars.get('BACKEND_CORS_ORIGINS', 'http://localhost:3000')
    )
    
    # API keys (masked)
    vision_api_key = get_input(
        "Landing.AI Vision Agent API key",
        default=existing_vars.get('VISION_AGENT_API_KEY', ''),
        is_secret=True
    )
    
    openai_api_key = get_input(
        "OpenAI API key",
        default=existing_vars.get('OPENAI_API_KEY', ''),
        is_secret=True
    )
    
    # Azure storage settings
    print("\n--- Storage Configuration ---")
    use_azure = get_input(
        "Use Azure Blob Storage?",
        default="yes" if existing_vars.get('STORAGE_MODE') == 'azure' else "no",
        choices=["yes", "no"]
    ).lower() == "yes"
    
    storage_mode = "azure" if use_azure else "local"
    
    azure_settings = {}
    if use_azure:
        print("\n--- Azure Blob Storage Configuration ---")
        azure_settings['AZURE_STORAGE_ACCOUNT_NAME'] = get_input(
            "Azure Storage Account Name",
            default=existing_vars.get('AZURE_STORAGE_ACCOUNT_NAME', '')
        )
        
        azure_settings['AZURE_STORAGE_ACCOUNT_KEY'] = get_input(
            "Azure Storage Account Key",
            default=existing_vars.get('AZURE_STORAGE_ACCOUNT_KEY', ''),
            is_secret=True
        )
        
        azure_settings['AZURE_STORAGE_CONTAINER_NAME'] = get_input(
            "Azure Storage Container Name",
            default=existing_vars.get('AZURE_STORAGE_CONTAINER_NAME', '')
        )
        
        azure_settings['AZURE_SAS_TTL_MINUTES'] = get_input(
            "Azure SAS token TTL (minutes)",
            default=existing_vars.get('AZURE_SAS_TTL_MINUTES', '60'),
            validator=validate_int
        )
    
    # Combine all settings
    backend_vars = {
        'APP_NAME': app_name,
        'APP_VERSION': app_version,
        'API_V1_STR': api_v1_str,
        'DATABASE_URL': database_url,
        'UPLOAD_DIRECTORY': upload_dir,
        'MAX_UPLOAD_SIZE': max_upload_size,
        'BACKEND_CORS_ORIGINS': cors_origins,
        'STORAGE_MODE': storage_mode,
        'VISION_AGENT_API_KEY': vision_api_key,
        'OPENAI_API_KEY': openai_api_key,
        'OPENAI_MODEL': existing_vars.get('OPENAI_MODEL', 'gpt-4-turbo-preview'),
        'OPENAI_MAX_TOKENS': existing_vars.get('OPENAI_MAX_TOKENS', '4096'),
        'OPENAI_TEMPERATURE': existing_vars.get('OPENAI_TEMPERATURE', '0.7')
    }
    
    # Add Azure settings if needed
    if use_azure:
        backend_vars.update(azure_settings)
    
    return backend_vars, storage_mode


def setup_frontend_env(storage_mode):
    """Interactive setup for frontend/.env file."""
    print("\n=== Frontend Environment Setup ===\n")
    
    # Load existing values if any
    frontend_env_path = 'frontend/.env'
    existing_vars = parse_env_file(frontend_env_path)
    
    # API URL
    api_url = get_input(
        "Backend API URL",
        default=existing_vars.get('VITE_API_URL', 'http://localhost:8000'),
        validator=validate_url
    )
    
    # Upload mode (should match backend storage mode)
    upload_mode = get_input(
        "Upload mode",
        default=storage_mode,
        choices=["local", "azure"]
    )
    
    # Combine settings
    frontend_vars = {
        'VITE_API_URL': api_url,
        'VITE_UPLOAD_MODE': upload_mode
    }
    
    return frontend_vars


def print_summary(backend_vars, frontend_vars):
    """Print a summary of the settings."""
    print("\n=== Configuration Summary ===\n")
    
    print("Backend Settings:")
    for key, value in sorted(backend_vars.items()):
        # Mask sensitive values
        if key in ['VISION_AGENT_API_KEY', 'OPENAI_API_KEY', 'AZURE_STORAGE_ACCOUNT_KEY']:
            if value:
                masked = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '****'
                print(f"  {key}: {masked}")
            else:
                print(f"  {key}: <empty>")
        else:
            print(f"  {key}: {value}")
    
    print("\nFrontend Settings:")
    for key, value in sorted(frontend_vars.items()):
        print(f"  {key}: {value}")


def main():
    """Main function to run the setup."""
    clear_screen()
    print("=== Apex ADE Environment Setup ===")
    print("This script will help you set up the environment variables for Apex ADE.")
    print("Press Enter to accept the default values shown in [brackets].")
    
    # Get backend settings
    backend_vars, storage_mode = setup_backend_env()
    
    # Get frontend settings
    frontend_vars = setup_frontend_env(storage_mode)
    
    # Print summary
    print_summary(backend_vars, frontend_vars)
    
    # Confirm and save
    confirm = get_input("\nSave these settings?", default="y", choices=["y", "n"]).lower()
    
    if confirm == "y":
        # Write backend .env
        write_env_file('backend/.env', backend_vars, header="Apex ADE Backend Environment")
        print(f"✅ Backend environment saved to backend/.env")
        
        # Write frontend .env
        write_env_file('frontend/.env', frontend_vars, header="Apex ADE Frontend Environment")
        print(f"✅ Frontend environment saved to frontend/.env")
        
        print("\n🚀 Setup complete! You can now run the application.")
    else:
        print("\n❌ Setup cancelled. No files were modified.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user. No files were modified.")
        sys.exit(1)
