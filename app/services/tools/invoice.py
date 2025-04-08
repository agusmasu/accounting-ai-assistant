from langchain_core.tools import tool

from app.models.invoice import Invoice
from app.services.tusfacturas_service import TusFacturasService

@tool
async def create_invoice(invoice_data: Invoice):
    """Create an invoice using the TusFacturas API
    
    Args:
        invoice_data (Invoice): The invoice data to create
        
    Returns:
        dict: The invoice data
    """
    tusfacturas_service = TusFacturasService()
    return await tusfacturas_service.generate_invoice(invoice_data)


