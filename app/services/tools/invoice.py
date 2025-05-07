from langchain_core.tools import tool

from app.models.invoice import InvoiceInputData
from app.services.tusfacturas import TusFacturasService
import logging
import asyncio

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class InvoiceToolsService:

    def __init__(self, tusfacturas_service: TusFacturasService):
        self.tusfacturas_service = tusfacturas_service

    @tool(name_or_callable="create_invoice_test", description="Create an invoice using the TusFacturas API")
    def create_invoice_test():
        """Create an invoice using the TusFacturas API
        
        Returns:
            dict: The invoice data
        """
        return "Invoice created wirh id 1"

    @tool(name_or_callable="create_invoice", description="Create an invoice using the TusFacturas API")
    def create_invoice(invoice_data: InvoiceInputData, user_id: str):
        """Create an invoice using the TusFacturas API
        
        Args:
            invoice_data (Invoice): The invoice data to create
            user_id (str): The user id of the user who is creating the invoice

        Returns:
            dict: The invoice data
        """
        
        # Print the invoice data
        logger.info(f"Creating invoice with the following data: {invoice_data}")

        tusfacturas_service = TusFacturasService()
        return asyncio.run(tusfacturas_service.generate_invoice(invoice_data, user_id))

