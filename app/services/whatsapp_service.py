import os
import requests
import hmac
import hashlib
from fastapi import Request
import aiohttp
import json
from typing import Dict, Optional

class WhatsAppService:
    def __init__(self):
        self.token = os.getenv("WHATSAPP_TOKEN")
        self.verify_token = "facturai_verify_token_123"
        self.api_version = "v17.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        # Store active conversation threads
        self.active_threads: Dict[str, str] = {}
        
    def verify_webhook(self, request: Request) -> bool:
        """Verify the webhook signature from WhatsApp"""
        # Check if this is a test request
        if request.query_params.get("test_mode") == "true":
            return True
            
        signature = request.headers.get("X-Hub-Signature-256")
        if not signature:
            return False
            
        body = request.body()
        expected_signature = hmac.new(
            self.verify_token.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, f"sha256={expected_signature}")
    
    def is_voice_message(self, data: dict) -> bool:
        """Check if the message is a voice message"""
        try:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            return message.get("type") == "audio"
        except (KeyError, IndexError):
            return False
    
    def is_text_message(self, data: dict) -> bool:
        """Check if the message is a text message"""
        try:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            return message.get("type") == "text"
        except (KeyError, IndexError):
            return False
    
    def is_image_message(self, data: dict) -> bool:
        """Check if the message is an image message"""
        try:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            return message.get("type") == "image"
        except (KeyError, IndexError):
            return False
    
    def get_text_content(self, data: dict) -> str:
        """Extract the text content from the webhook data"""
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        return message["text"]["body"]
    
    def get_sender_phone(self, data: dict) -> str:
        """Extract the sender's phone number from the webhook data"""
        return data["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
    
    def get_voice_url(self, data: dict) -> str:
        """Extract the voice message URL from the webhook data"""
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        return message["audio"]["id"]
    
    def get_image_id(self, data: dict) -> str:
        """Extract the image ID from the webhook data"""
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        return message["image"]["id"]
    
    async def download_voice(self, voice_id: str) -> bytes:
        """Download the voice message from WhatsApp"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/{voice_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception("Failed to download voice message")
                return await response.read()
    
    async def download_image(self, image_id: str) -> bytes:
        """Download the image from WhatsApp"""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/{image_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception("Failed to download image")
                return await response.read()
    
    async def send_message(self, to: str, message: str):
        """Send a message back to the user"""
        url = f"{self.base_url}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": message}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    raise Exception("Failed to send message")
    
    async def send_document(self, to: str, document_url: str, caption: str = None):
        """
        Send a document (like a PDF) to the user
        
        Args:
            to: The recipient's phone number
            document_url: URL to the document
            caption: Optional caption for the document
        """
        url = f"{self.base_url}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "document",
            "document": {
                "link": document_url
            }
        }
        
        if caption:
            data["document"]["caption"] = caption
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    raise Exception("Failed to send document")
    
    def handle_verification(self, request: Request):
        """Handle WhatsApp webhook verification"""
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        if mode and token:
            if mode == "subscribe" and token == self.verify_token:
                return int(challenge)
            return "Invalid verification token"
        return "Invalid request"
    
    def get_thread_id(self, phone_number: str) -> str:
        """
        Get or create a thread ID for a phone number
        """
        if phone_number not in self.active_threads:
            self.active_threads[phone_number] = f"whatsapp_{phone_number}"
        return self.active_threads[phone_number] 