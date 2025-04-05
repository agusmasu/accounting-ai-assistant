import pytest
import logging
from datetime import datetime
from app.services.tusfacturas_service import TusFacturasService
from app.models.invoice import Invoice, InvoiceItem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def tusfacturas_service():
    """Fixture to create a TusFacturasService instance"""
    return TusFacturasService()

@pytest.fixture
def sample_invoice():
    """Fixture to create a sample invoice for testing"""
    return Invoice(
        customer_name="Test Company S.A.",
        customer_tax_id="30712345678",
        customer_address="Av. Test 123, CABA",
        items=[
            InvoiceItem(
                description="Test Product 1",
                quantity=2,
                unit_price=1000.00,
                tax_rate=0.21
            ),
            InvoiceItem(
                description="Test Product 2",
                quantity=1,
                unit_price=500.00,
                tax_rate=0.21
            )
        ],
        invoice_date=datetime.now(),
        invoice_type="A",
        payment_method="Transfer",
        currency="ARS"
    )

@pytest.mark.asyncio
async def test_generate_invoice(tusfacturas_service, sample_invoice):
    """Test invoice generation with TusFacturasApp"""
    try:
        # Log test data
        logger.info("Starting invoice generation test")
        logger.info(f"Sample invoice data: {sample_invoice.model_dump()}")

        # Generate invoice
        response = await tusfacturas_service.generate_invoice(sample_invoice)

        # Log response
        logger.info(f"API response: {response}")

        # Verify response structure and required fields according to API docs
        assert response is not None, "Response should not be None"
        assert isinstance(response, dict), "Response should be a dictionary"
        
        # Required fields for successful response
        required_fields = [
            "invoice_number", "status", "pdf_url", "cae", "cae_vto",
            "total", "tipo", "punto_venta"
        ]
        for field in required_fields:
            assert field in response, f"Response should contain {field}"

        # Verify response values
        assert response["status"] == "success", "Status should be success"
        assert response["invoice_number"] is not None, "Invoice number should not be None"
        assert response["pdf_url"] is not None, "PDF URL should not be None"
        assert response["cae"] is not None, "CAE should not be None"
        assert response["cae_vto"] is not None, "CAE expiration date should not be None"
        assert response["total"] is not None, "Total amount should not be None"
        assert response["tipo"] == "FACTURA A", "Invoice type should match request"
        assert response["punto_venta"] == "1", "Point of sale should match request"

        print("\nInvoice generated successfully!")
        print(f"Invoice number: {response['invoice_number']}")
        print(f"Invoice type: {response['tipo']}")
        print(f"Point of sale: {response['punto_venta']}")
        print(f"Total amount: {response['total']}")
        print(f"PDF URL: {response['pdf_url']}")
        print(f"CAE: {response['cae']}")
        print(f"CAE expiration: {response['cae_vto']}")

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        pytest.fail(f"Failed to generate invoice: {str(e)}")

@pytest.mark.asyncio
async def test_invalid_invoice(tusfacturas_service):
    """Test invoice generation with invalid data"""
    try:
        # Create invalid invoice (missing required fields)
        invalid_invoice = Invoice(
            customer_name="",  # Empty name
            customer_tax_id="",  # Empty tax ID
            customer_address="",  # Empty address
            items=[],  # Empty items
            invoice_date=datetime.now(),
            invoice_type="A",
            payment_method="Transfer",
            currency="ARS"
        )

        # Attempt to generate invoice
        with pytest.raises(Exception) as exc_info:
            await tusfacturas_service.generate_invoice(invalid_invoice)

        # Verify error message format according to API docs
        error_message = str(exc_info.value)
        assert "TusFacturasApp error" in error_message, "Error should be from TusFacturasApp"
        
        logger.info(f"Test passed: Invalid invoice correctly rejected with error: {error_message}")

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        pytest.fail(f"Test failed: {str(e)}") 