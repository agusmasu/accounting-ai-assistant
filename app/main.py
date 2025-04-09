from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from .services.whatsapp_service import WhatsAppService
from .services.ai_service import AIService
from .services.tusfacturas_service import TusFacturasService
from .models.invoice import InvoiceInputData

# Load environment variables
load_dotenv()

app = FastAPI(title="FacturAI API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
whatsapp_service = WhatsAppService()
ai_service = AIService()
tusfacturas_service = TusFacturasService()

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Webhook endpoint for WhatsApp messages
    """
    try:
        # Verify WhatsApp webhook
        if not whatsapp_service.verify_webhook(request):
            raise HTTPException(status_code=403, detail="Invalid webhook signature")

        # Get message data
        data = await request.json()
        
        # Process voice message
        if whatsapp_service.is_voice_message(data):
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
                f"Invoice generated successfully!\nInvoice number: {invoice_response['invoice_number']}\nPDF: {invoice_response['pdf_url']}"
            )
            
            return {"status": "success"}
            
        return {"status": "ignored", "message": "Not a voice message"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/webhook/whatsapp")
async def verify_webhook(request: Request):
    """
    Verify WhatsApp webhook
    """
    return whatsapp_service.handle_verification(request) 