#!/usr/bin/env python3
"""
Idempotent deployment script for Apex ADE.
Validates environment, manages git operations, and triggers deployments.
"""
import os
import sys
import argparse
import subprocess
import json
import re
import time
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Deploy Apex ADE")
    parser.add_argument(
        "--branch", 
        default="droid/deploy",
        help="Branch name to use (default: droid/deploy)"
    )
    parser.add_argument(
        "--push", 
        action="store_true",
        help="Push changes to remote"
    )
    parser.add_argument(
        "--ensure-azure", 
        action="store_true",
        help="Ensure Azure container exists (if STORAGE_MODE=azure)"
    )
    parser.add_argument(
        "--trigger-render", 
        action="store_true",
        help="Trigger Render deploys via API (requires env vars)"
    )
    parser.add_argument(
        "--render-backend-id",
        help="Render backend service ID (optional if env RENDER_BACKEND_SERVICE_ID is set)"
    )
    parser.add_argument(
        "--render-frontend-id",
        help="Render frontend service ID (optional if env RENDER_FRONTEND_SERVICE_ID is set)"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Print actions but do not execute"
    )
    
    return parser.parse_args()


def log(message: str, level: str = "INFO", dry_run: bool = False):
    """Log a message with a level prefix."""
    prefix = f"[{level}]"
    if dry_run and level == "ACTION":
        prefix = "[DRY-RUN]"
    print(f"{prefix} {message}")


def run_command(
    cmd: List[str], 
    cwd: Optional[str] = None, 
    dry_run: bool = False, 
    capture_output: bool = False
) -> Tuple[int, str]:
    """
    Run a shell command with proper error handling.
    
    Args:
        cmd: Command and arguments as a list
        cwd: Working directory
        dry_run: If True, only print the command
        capture_output: If True, capture and return stdout
        
    Returns:
        Tuple of (return_code, output)
    """
    cmd_str = " ".join(cmd)
    
    if dry_run:
        log(f"Would run: {cmd_str}", "ACTION", dry_run)
        return 0, ""
        
    log(f"Running: {cmd_str}", "INFO")
    
    try:
        if capture_output:
            result = subprocess.run(
                cmd, 
                cwd=cwd,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return result.returncode, result.stdout
        else:
            result = subprocess.run(cmd, cwd=cwd, check=False)
            return result.returncode, ""
    except Exception as e:
        log(f"Command failed: {e}", "ERROR")
        return 1, ""


def get_repo_root() -> str:
    """Get the git repository root directory."""
    code, output = run_command(
        ["git", "rev-parse", "--show-toplevel"], 
        capture_output=True
    )
    
    if code != 0:
        log("Failed to find git repository root", "ERROR")
        sys.exit(1)
        
    return output.strip()


def parse_env_file(file_path: str) -> Dict[str, str]:
    """Parse an .env file into a dictionary."""
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
                # Strip quotes if present
                value = value.strip()
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                    
                env_vars[key.strip()] = value
                
    return env_vars


def validate_env_files() -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Validate that environment files exist and contain required settings.
    
    Returns:
        Tuple of (backend_env, frontend_env)
    """
    repo_root = get_repo_root()
    backend_env_path = os.path.join(repo_root, "backend", ".env")
    frontend_env_path = os.path.join(repo_root, "frontend", ".env")
    
    # Check if files exist
    if not os.path.exists(backend_env_path):
        log(f"Backend .env file not found at {backend_env_path}", "ERROR")
        log("Run scripts/setup_envs.py to create environment files", "INFO")
        sys.exit(1)
        
    if not os.path.exists(frontend_env_path):
        log(f"Frontend .env file not found at {frontend_env_path}", "ERROR")
        log("Run scripts/setup_envs.py to create environment files", "INFO")
        sys.exit(1)
        
    # Parse env files
    backend_env = parse_env_file(backend_env_path)
    frontend_env = parse_env_file(frontend_env_path)
    
    # Validate backend env
    required_backend_vars = ["VISION_AGENT_API_KEY", "OPENAI_API_KEY"]
    missing_backend_vars = [var for var in required_backend_vars if not backend_env.get(var)]
    
    if missing_backend_vars:
        log(f"Missing required backend environment variables: {', '.join(missing_backend_vars)}", "ERROR")
        log("Run scripts/setup_envs.py to update environment files", "INFO")
        sys.exit(1)
        
    # If using Azure storage, check for Azure settings
    if backend_env.get("STORAGE_MODE") == "azure":
        required_azure_vars = [
            "AZURE_STORAGE_ACCOUNT_NAME",
            "AZURE_STORAGE_ACCOUNT_KEY",
            "AZURE_STORAGE_CONTAINER_NAME"
        ]
        missing_azure_vars = [var for var in required_azure_vars if not backend_env.get(var)]
        
        if missing_azure_vars:
            log(f"STORAGE_MODE is set to 'azure' but missing required Azure variables: {', '.join(missing_azure_vars)}", "ERROR")
            log("Run scripts/setup_envs.py to update environment files", "INFO")
            sys.exit(1)
    
    # Validate frontend env
    required_frontend_vars = ["VITE_API_URL", "VITE_UPLOAD_MODE"]
    missing_frontend_vars = [var for var in required_frontend_vars if not frontend_env.get(var)]
    
    if missing_frontend_vars:
        log(f"Missing required frontend environment variables: {', '.join(missing_frontend_vars)}", "ERROR")
        log("Run scripts/setup_envs.py to update environment files", "INFO")
        sys.exit(1)
        
    # Check consistency between backend and frontend
    if backend_env.get("STORAGE_MODE") != frontend_env.get("VITE_UPLOAD_MODE"):
        log(f"Warning: Backend STORAGE_MODE ({backend_env.get('STORAGE_MODE')}) doesn't match frontend VITE_UPLOAD_MODE ({frontend_env.get('VITE_UPLOAD_MODE')})", "WARNING")
        
    return backend_env, frontend_env


def ensure_azure_container(backend_env: Dict[str, str], dry_run: bool = False) -> bool:
    """
    Ensure Azure container exists if STORAGE_MODE is azure.
    
    Args:
        backend_env: Backend environment variables
        dry_run: If True, only print actions
        
    Returns:
        True if container exists or was created, False otherwise
    """
    if backend_env.get("STORAGE_MODE") != "azure":
        log("STORAGE_MODE is not 'azure', skipping Azure container check", "INFO")
        return True
        
    try:
        # Import azure-storage-blob only when needed
        from azure.storage.blob import BlobServiceClient
        from azure.core.exceptions import ResourceExistsError
    except ImportError:
        log("azure-storage-blob package not installed. Run: pip install azure-storage-blob", "ERROR")
        return False
        
    account_name = backend_env.get("AZURE_STORAGE_ACCOUNT_NAME")
    account_key = backend_env.get("AZURE_STORAGE_ACCOUNT_KEY")
    container_name = backend_env.get("AZURE_STORAGE_CONTAINER_NAME")
    
    if dry_run:
        log(f"Would check if Azure container '{container_name}' exists in account '{account_name}'", "ACTION", dry_run)
        return True
        
    log(f"Checking if Azure container '{container_name}' exists...", "INFO")
    
    try:
        # Create connection string
        conn_str = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
        
        # Create blob service client
        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        
        # Check if container exists
        container_client = blob_service_client.get_container_client(container_name)
        properties = container_client.get_container_properties()
        
        log(f"Azure container '{container_name}' exists", "INFO")
        return True
    except ResourceExistsError:
        # Container already exists (shouldn't happen in this flow but included for completeness)
        log(f"Azure container '{container_name}' already exists", "INFO")
        return True
    except Exception as e:
        if "ContainerNotFound" in str(e):
            log(f"Azure container '{container_name}' not found, creating...", "INFO")
            try:
                # Create container
                blob_service_client = BlobServiceClient.from_connection_string(conn_str)
                blob_service_client.create_container(container_name)
                log(f"Azure container '{container_name}' created successfully", "INFO")
                return True
            except Exception as create_error:
                log(f"Failed to create Azure container: {create_error}", "ERROR")
                return False
        else:
            log(f"Error checking Azure container: {e}", "ERROR")
            return False


def handle_git_operations(branch: str, push: bool, dry_run: bool) -> bool:
    """
    Handle git operations: check status, commit changes, create/checkout branch, push.
    
    Args:
        branch: Branch name to use
        push: Whether to push changes to remote
        dry_run: If True, only print actions
        
    Returns:
        True if successful, False otherwise
    """
    repo_root = get_repo_root()
    
    # Check if there are changes to commit
    code, status_output = run_command(
        ["git", "status", "--porcelain"], 
        cwd=repo_root,
        capture_output=True
    )
    
    has_changes = bool(status_output.strip())
    
    if has_changes:
        log("Uncommitted changes detected", "INFO")
        
        # Add all changes
        code, _ = run_command(
            ["git", "add", "."],
            cwd=repo_root,
            dry_run=dry_run
        )
        
        if code != 0 and not dry_run:
            log("Failed to add changes", "ERROR")
            return False
            
        # Commit changes
        commit_message = f"Automated deployment commit - {time.strftime('%Y-%m-%d %H:%M:%S')}"
        code, _ = run_command(
            ["git", "commit", "-m", commit_message],
            cwd=repo_root,
            dry_run=dry_run
        )
        
        if code != 0 and not dry_run:
            log("Failed to commit changes", "ERROR")
            return False
            
        log("Changes committed successfully", "INFO")
    else:
        log("No changes to commit", "INFO")
    
    # Check if branch exists
    code, branches_output = run_command(
        ["git", "branch"],
        cwd=repo_root,
        capture_output=True
    )
    
    branch_exists = any(b.strip().replace("* ", "") == branch for b in branches_output.split("\n"))
    current_branch = next((b.strip().replace("* ", "") for b in branches_output.split("\n") if b.startswith("* ")), None)
    
    # Create or checkout branch
    if current_branch != branch:
        if branch_exists:
            # Branch exists, checkout
            code, _ = run_command(
                ["git", "checkout", branch],
                cwd=repo_root,
                dry_run=dry_run
            )
            
            if code != 0 and not dry_run:
                log(f"Failed to checkout branch '{branch}'", "ERROR")
                return False
                
            log(f"Checked out existing branch '{branch}'", "INFO")
        else:
            # Create new branch
            code, _ = run_command(
                ["git", "checkout", "-b", branch],
                cwd=repo_root,
                dry_run=dry_run
            )
            
            if code != 0 and not dry_run:
                log(f"Failed to create branch '{branch}'", "ERROR")
                return False
                
            log(f"Created and checked out new branch '{branch}'", "INFO")
    else:
        log(f"Already on branch '{branch}'", "INFO")
    
    # Push changes if requested
    if push:
        code, _ = run_command(
            ["git", "push", "--set-upstream", "origin", branch],
            cwd=repo_root,
            dry_run=dry_run
        )
        
        if code != 0 and not dry_run:
            log("Failed to push changes", "ERROR")
            return False
            
        log(f"Changes pushed to '{branch}'", "INFO")
    
    return True


def trigger_render_deploy(
    service_id: str, 
    api_key: str, 
    service_type: str, 
    dry_run: bool = False
) -> bool:
    """
    Trigger a deploy on Render.
    
    Args:
        service_id: Render service ID
        api_key: Render API key
        service_type: Service type (backend or frontend)
        dry_run: If True, only print actions
        
    Returns:
        True if successful, False otherwise
    """
    if not service_id:
        log(f"No Render {service_type} service ID provided, skipping", "WARNING")
        return False
        
    if dry_run:
        log(f"Would trigger deploy for Render {service_type} service {service_id}", "ACTION", dry_run)
        return True
        
    log(f"Triggering deploy for Render {service_type} service {service_id}", "INFO")
    
    url = f"https://api.render.com/v1/services/{service_id}/deploys"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = json.dumps({"clearCache": True}).encode("utf-8")
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode("utf-8"))
            deploy_id = response_data.get("id", "unknown")
            log(f"Render {service_type} deploy triggered successfully. Deploy ID: {deploy_id}", "INFO")
            return True
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            error_json = json.loads(error_body)
            error_message = error_json.get("message", error_body)
        except:
            error_message = error_body
            
        log(f"Failed to trigger Render {service_type} deploy: {e.code} {error_message}", "ERROR")
        return False
    except Exception as e:
        log(f"Error triggering Render {service_type} deploy: {e}", "ERROR")
        return False


def main():
    """Main function to orchestrate deployment."""
    args = parse_arguments()
    
    log("Starting Apex ADE deployment", "INFO")
    
    # Validate environment files
    log("Validating environment files...", "INFO")
    backend_env, frontend_env = validate_env_files()
    log("Environment files validated successfully", "INFO")
    
    # Ensure Azure container if requested
    if args.ensure_azure and backend_env.get("STORAGE_MODE") == "azure":
        log("Ensuring Azure container exists...", "INFO")
        if not ensure_azure_container(backend_env, args.dry_run):
            log("Failed to ensure Azure container exists", "ERROR")
            sys.exit(1)
        log("Azure container check completed", "INFO")
    
    # Handle git operations
    log("Handling git operations...", "INFO")
    if not handle_git_operations(args.branch, args.push, args.dry_run):
        log("Failed to complete git operations", "ERROR")
        sys.exit(1)
    log("Git operations completed successfully", "INFO")
    
    # Trigger Render deploys if requested
    if args.trigger_render:
        log("Triggering Render deploys...", "INFO")
        
        # Get Render API key
        render_api_key = os.environ.get("RENDER_API_KEY")
        if not render_api_key:
            log("RENDER_API_KEY environment variable not set", "ERROR")
            sys.exit(1)
        
        # Get backend service ID
        backend_service_id = args.render_backend_id or os.environ.get("RENDER_BACKEND_SERVICE_ID")
        if backend_service_id:
            trigger_render_deploy(backend_service_id, render_api_key, "backend", args.dry_run)
        else:
            log("No Render backend service ID provided, skipping backend deploy", "WARNING")
        
        # Get frontend service ID
        frontend_service_id = args.render_frontend_id or os.environ.get("RENDER_FRONTEND_SERVICE_ID")
        if frontend_service_id:
            trigger_render_deploy(frontend_service_id, render_api_key, "frontend", args.dry_run)
        else:
            log("No Render frontend service ID provided, skipping frontend deploy", "WARNING")
        
        log("Render deploy triggers completed", "INFO")
    
    log("Deployment completed successfully", "INFO")
    
    # Print next steps
    if args.push:
        log(f"Changes pushed to branch '{args.branch}'", "INFO")
        if not args.trigger_render:
            log("To deploy to Render, either:", "INFO")
            log("1. Set up auto-deploy from this branch in the Render dashboard", "INFO")
            log("2. Run this script again with --trigger-render and provide service IDs", "INFO")
    else:
        log(f"Changes committed to branch '{args.branch}' but not pushed", "INFO")
        log("To push changes and deploy, run:", "INFO")
        log(f"  python scripts/deploy.py --branch {args.branch} --push [--trigger-render]", "INFO")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\nDeployment cancelled by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        log(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)
