import os
import json
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import functions_framework
from app.services.whatsapp_service import WhatsAppService
from app.services.ai_service import AIService
from app.services.tusfacturas_service import TusFacturasService
from app.models.invoice import InvoiceInputData

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="FacturAI API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

# Initialize services
whatsapp_service = WhatsAppService()
ai_service = AIService()
tusfacturas_service = TusFacturasService()

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Webhook endpoint for WhatsApp messages
    """
    logger.info(f"Received request from a WhatsApp webhook, POST request")
    try:
        # Check if this is a test request
        is_test_mode = request.query_params.get("test_mode") == "true"
        if is_test_mode:
            logger.info("Test mode enabled - bypassing signature verification")
        
        # Verify WhatsApp webhook
        if not whatsapp_service.verify_webhook(request):
            logger.warn("Invalid webhook signature")
            raise HTTPException(status_code=403, detail="Invalid webhook signature")

        # Get message data
        data = await request.json()
        
        # Process voice message
        if whatsapp_service.is_voice_message(data):
            logger.info("Processing voice message")
            # Download voice message
            voice_url = whatsapp_service.get_voice_url(data)
            voice_file = await whatsapp_service.download_voice(voice_url)
            
            # Process voice with AI
            invoice_data = await ai_service.process_voice(voice_file)
            
            # Generate invoice using TusFacturasApp
            invoice = InvoiceInputData(**invoice_data)
            invoice_response = await tusfacturas_service.generate_invoice(invoice)
            
            # Send confirmation message with PDF link
            await whatsapp_service.send_message(
                data["entry"][0]["changes"][0]["value"]["messages"][0]["from"],
                f"Invoice generated successfully!\nInvoice number: {invoice_response['invoice_number']}"
            )
            
            # Send the PDF document
            await whatsapp_service.send_document(
                data["entry"][0]["changes"][0]["value"]["messages"][0]["from"],
                invoice_response["pdf_url"],
                f"Invoice #{invoice_response['invoice_number']}"
            )
            
            return {"status": "success"}
        
        # Process text message
        elif whatsapp_service.is_text_message(data):
            logger.info("Processing text message")
            # Get the sender's phone number and message content
            sender_phone = whatsapp_service.get_sender_phone(data)
            message_text = whatsapp_service.get_text_content(data)
            
            # Get the thread ID for this user
            thread_id = whatsapp_service.get_thread_id(sender_phone)
            
            # Process the message with the AI agent
            response = await ai_service.process_text(message_text, thread_id)
            
            # Send the AI response back to WhatsApp
            await whatsapp_service.send_message(sender_phone, response["response"])
            
            return {"status": "success"}
        
        # Process image message (for future invoice processing)
        elif whatsapp_service.is_image_message(data):
            # Get the sender's phone number and image ID
            sender_phone = whatsapp_service.get_sender_phone(data)
            image_id = whatsapp_service.get_image_id(data)
            
            # Download the image
            image_data = await whatsapp_service.download_image(image_id)
            
            # For now, just acknowledge receipt of the image
            # In the future, this could be used to process invoice images
            await whatsapp_service.send_message(
                sender_phone,
                "I received your image. Image processing for invoices will be available soon!"
            )
            
            return {"status": "success"}
            
        return {"status": "ignored", "message": "Not a supported message type"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/webhook/whatsapp")
async def verify_webhook(request: Request):
    """
    Verify WhatsApp webhook
    """
    return whatsapp_service.handle_verification(request)

# Cloud Functions entry point
@functions_framework.http
def whatsapp_webhook_function(request):
    """
    Cloud Functions entry point for WhatsApp webhook
    """
    logger.info("Received request in Cloud Function")
    # Convert the request to a FastAPI request
    fastapi_request = Request(scope=request.environ)
    
    # Handle the request based on the method
    if request.method == "GET":
        return verify_webhook(fastapi_request)
    elif request.method == "POST":
        return whatsapp_webhook(fastapi_request)
    else:
        return {"status": "error", "message": "Method not allowed"} 