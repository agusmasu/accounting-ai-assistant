from langchain_core.tools import tool

from app.models.invoice import InvoiceInputData
from app.services.tusfacturas_service import TusFacturasService

@tool
async def create_invoice(invoice_data: InvoiceInputData):
    """Create an invoice using the TusFacturas API
    
    Args:
        invoice_data (Invoice): The invoice data to create
        
    Returns:
        dict: The invoice data
    """
    
    # Print the invoice data
    print("Creating invoice with the following data:")
    print(invoice_data)

    tusfacturas_service = TusFacturasService()
    return await tusfacturas_service.generate_invoice(invoice_data)


