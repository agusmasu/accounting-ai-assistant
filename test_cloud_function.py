#!/usr/bin/env python3
import requests
import json
import argparse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_text_message(function_url, phone_number, message):
    """Send a simulated text message to the Cloud Function"""
    webhook_url = f"{function_url}/webhook/whatsapp?test_mode=true"
    
    # Create a simulated WhatsApp webhook payload
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456789",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "1234567890",
                                "phone_number_id": "123456789"
                            },
                            "messages": [
                                {
                                    "from": phone_number,
                                    "id": "wamid.123456789",
                                    "timestamp": "1234567890",
                                    "text": {
                                        "body": message
                                    },
                                    "type": "text"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
    
    # Send the request
    print(f"Sending request to: {webhook_url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(webhook_url, json=payload)
    
    # Print the response
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    return response

def verify_webhook(function_url):
    """Verify the webhook"""
    webhook_url = f"{function_url}/webhook/whatsapp"
    
    # Get the verify token from environment variables
    verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "facturai_verify_token_123")
    
    # Create a simulated verification request
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": verify_token,
        "hub.challenge": "1234567890"
    }
    
    # Send the request
    print(f"Sending verification request to: {webhook_url}")
    print(f"Params: {params}")
    
    response = requests.get(webhook_url, params=params)
    
    # Print the response
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    
    return response

def main():
    parser = argparse.ArgumentParser(description="Test Cloud Function WhatsApp webhook")
    parser.add_argument("--url", required=True, help="Cloud Function URL (e.g., https://your-function-url)")
    parser.add_argument("--phone", default="1234567890", help="Phone number to simulate (default: 1234567890)")
    parser.add_argument("--message", default="Hello, FacturAI!", help="Message to send (default: Hello, FacturAI!)")
    parser.add_argument("--type", choices=["text", "verify"], default="text", help="Type of request to send (default: text)")
    
    args = parser.parse_args()
    
    if args.type == "text":
        send_text_message(args.url, args.phone, args.message)
    elif args.type == "verify":
        verify_webhook(args.url)

if __name__ == "__main__":
    main() 