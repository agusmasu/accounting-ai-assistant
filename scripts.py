#!/usr/bin/env python3
import os
import subprocess
import click
import sys

@click.group()
def cli():
    """Command runner for the accounting-ai-assistant project."""
    pass

@cli.command()
def start():
    """Run the cloud functions server locally."""
    # Set environment variables from .env file
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Run the functions framework using the Python module approach
    port = int(os.environ.get("PORT", 8080))
    subprocess.run([
        sys.executable, "-m", "functions_framework",
        "--target=http_function",
        "--source=main_functions.py",
        f"--port={port}",
        "--debug"
    ], check=True)

@cli.command()
def fastapi():
    """Run the FastAPI server."""
    subprocess.run(['uvicorn', 'app.main:app', '--reload'], check=True)

@cli.command()
def console():
    """Run the console chat interface."""
    subprocess.run(['python', '-m', 'app.console_chat'], check=True)

@cli.command()
def deploy():
    """Deploy the function to Google Cloud."""
    subprocess.run(['./deploy_functions.sh'], check=True)

if __name__ == '__main__':
    cli() 