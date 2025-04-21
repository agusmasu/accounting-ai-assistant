"""Chat API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.ai import AIService
from app.services.tusfacturas import TusFacturasService
from app.api.deps import get_ai_service, get_tusfacturas_service
from typing import Dict, Any, Optional, List
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Request model for chat messages."""
    message: str
    thread_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat messages."""
    response: str
    thread_id: str
    tool_outputs: List[Dict[str, Any]] = []


class CreateInvoiceRequest(BaseModel):
    """Request model for invoice creation from chat output."""
    thread_id: str
    invoice_data: Dict[str, Any]


class InvoiceResponse(BaseModel):
    """Response model for invoice creation."""
    invoice_number: str
    pdf_url: str


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Send a message to the AI assistant and get a response.
    
    If no thread_id is provided, a new conversation thread will be created.
    """
    # Generate thread_id if not provided
    if not request.thread_id:
        request.thread_id = f"api_chat_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Process with AI
    result = await ai_service.process_text(request.message, request.thread_id)
    
    # Extract response and determine if invoice data is available
    response_text = result.get("response", "")
    tool_outputs = result.get("tool_outputs", [])
    
    return ChatResponse(
        response=response_text,
        thread_id=request.thread_id,
        tool_outputs=tool_outputs
    )


@router.post("/create-invoice", response_model=InvoiceResponse)
async def create_invoice(
    request: CreateInvoiceRequest,
    tusfacturas_service: TusFacturasService = Depends(get_tusfacturas_service)
):
    """
    Create an invoice using the invoice data from a previous chat response.
    """
    try:
        # Generate invoice
        invoice_response = await tusfacturas_service.generate_invoice(request.invoice_data)
        
        return InvoiceResponse(
            invoice_number=invoice_response["invoice_number"],
            pdf_url=invoice_response["pdf_url"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 