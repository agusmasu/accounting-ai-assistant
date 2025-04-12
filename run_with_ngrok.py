#!/usr/bin/env python3
import os
import subprocess
import time
import signal
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the verify token from environment variables or generate a random one
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "facturai_verify_token_123")

def print_banner():
    """Print a banner with instructions"""
    print("\n" + "="*80)
    print("FacturAI WhatsApp Integration".center(80))
    print("="*80)
    print(f"\nVerify Token: {VERIFY_TOKEN}")
    print("\nAdd this token to your .env file as WHATSAPP_VERIFY_TOKEN")
    print("or use it when configuring your WhatsApp webhook.")
    print("\nThe webhook URL will be displayed below when ngrok starts.")
    print("="*80 + "\n")

def start_ngrok(port):
    """Start ngrok and return the public URL"""
    # Start ngrok in a subprocess
    ngrok_process = subprocess.Popen(
        ["ngrok", "http", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for ngrok to start
    time.sleep(2)
    
    # Get the public URL from ngrok's API
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        tunnels = response.json()["tunnels"]
        for tunnel in tunnels:
            if tunnel["proto"] == "https":
                return tunnel["public_url"], ngrok_process
    except Exception as e:
        print(f"Error getting ngrok URL: {e}")
        return None, ngrok_process
    
    return None, ngrok_process

def start_uvicorn(port):
    """Start the FastAPI server using uvicorn"""
    return subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

def main():
    # Print banner with instructions
    print_banner()
    
    # Set the verify token in environment variables
    os.environ["WHATSAPP_VERIFY_TOKEN"] = VERIFY_TOKEN
    
    # Start the FastAPI server
    port = 8000
    uvicorn_process = start_uvicorn(port)
    print(f"Starting FastAPI server on port {port}...")
    
    # Start ngrok
    ngrok_url, ngrok_process = start_ngrok(port)
    
    if ngrok_url:
        webhook_url = f"{ngrok_url}/webhook/whatsapp"
        print("\n" + "="*80)
        print("WHATSAPP WEBHOOK URL".center(80))
        print("="*80)
        print(f"\n{webhook_url}\n")
        print("Add this URL to your WhatsApp webhook configuration.")
        print("="*80 + "\n")
    else:
        print("Failed to get ngrok URL. Check if ngrok is running correctly.")
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print("\nShutting down...")
        ngrok_process.terminate()
        uvicorn_process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main() 