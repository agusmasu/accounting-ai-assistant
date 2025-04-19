import functions_framework
from app.main import app
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask, request, redirect
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a Flask app for the function
flask_app = Flask(__name__)

# This provides a Flask-based function for Cloud Functions
@functions_framework.http
def http_function(request):
    """HTTP Cloud Function entry point."""
    # If this is a request to /docs or /openapi.json, use FastAPI directly
    path_info = request.environ.get("PATH_INFO", "")
    
    # We wrap FastAPI with a WSGI adapter to make it work with Functions Framework
    with flask_app.request_context(request.environ):
        return WSGIMiddleware(app)(request.environ, flask_app.response_class)

# If this script is run directly, start a local development server with Functions Framework
if __name__ == "__main__":
    # This is used when running locally
    import subprocess
    import sys
    
    # Default port is 8080 for Cloud Functions emulator
    port = int(os.environ.get("PORT", 8080))
    
    # Run the functions framework emulator 
    subprocess.run([
        sys.executable, "-m", "functions_framework",
        "--target=http_function",
        f"--port={port}",
        "--debug"
    ]) 