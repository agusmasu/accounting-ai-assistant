from langchain_core.tools import tool

from app.models.invoice import InvoiceInputData
from app.services.tusfacturas import TusFacturasService
from app.services.context import ContextService
import logging
import asyncio

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@tool(name_or_callable="create_invoice_test", description="Create an invoice using the TusFacturas API")
def create_invoice_test():
    """Create an invoice using the TusFacturas API

    Returns:
        dict: The invoice data
    """
    return "Invoice created wirh id 1"

@tool(name_or_callable="create_invoice", description="Create an invoice using the TusFacturas API")
def create_invoice(invoice_data: InvoiceInputData):
    """Create an invoice using the TusFacturas API

    Args:
        invoice_data (Invoice): The invoice data to create

    Returns:
        dict: The invoice data
    """

    # Get current user from context
    user = ContextService.get_current_user()
    if not user:
        logger.error("No user found in context")
        return {"error": "No user found in context. Cannot create invoice."}

    # Print the invoice data
    logger.info(f"Creating invoice with the following data: {invoice_data}")
    logger.info(f"Using user id from context: {user.id}")

    tusfacturas_service = TusFacturasService()
    return asyncio.run(tusfacturas_service.generate_invoice(invoice_data, user))

