import os
import logging
from typing import Dict, Any, List
import aiohttp
from datetime import datetime
from dotenv import load_dotenv
from app.models.invoice import Invoice, InvoiceItem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TusFacturasService:
    def __init__(self):
        """Initialize TusFacturasApp service with API credentials"""
        load_dotenv()
        self.api_url = "https://www.tusfacturas.app/app/api/v2/facturacion"
        self.api_key = os.getenv("TUSFACTURAS_API_KEY")
        self.api_token = os.getenv("TUSFACTURAS_API_TOKEN")
        self.user_token = os.getenv("TUSFACTURAS_USER_TOKEN")

        if not all([self.api_key, self.api_token, self.user_token]):
            raise ValueError("Missing required TusFacturasApp credentials in environment variables")

        logger.info("TusFacturasService initialized with:")
        logger.info(f"API URL: {self.api_url}")
        logger.info(f"API Key: {self.api_key}")
        logger.info(f"API Token: {self.api_token}")
        logger.info(f"User Token: {self.user_token}")

    def _prepare_items(self, items: List[InvoiceItem]) -> List[Dict[str, Any]]:
        """Format invoice items according to TusFacturasApp specifications"""
        formatted_items = [
            {
                "descripcion": item.description,
                "cantidad": str(item.quantity),
                "precio_unitario": str(item.unit_price),
                "alicuota": str(int(item.tax_rate * 100)),  # Convert decimal to percentage
                "unidad_medida": "7",  # Units
                "producto": {
                    "descripcion": item.description,
                    "codigo": "001",  # Default product code
                    "precio_unitario_sin_iva": str(item.unit_price)
                }
            }
            for item in items
        ]
        logger.info(f"Formatted items: {formatted_items}")
        return formatted_items

    async def generate_invoice(self, invoice: Invoice) -> Dict[str, Any]:
        """Generate an invoice using TusFacturasApp API"""
        try:
            # Prepare invoice data according to TusFacturasApp format
            invoice_data = {
                "usertoken": self.user_token,
                "apitoken": self.api_token,
                "apikey": self.api_key,
                "cliente": {
                    "documento_tipo": "CUIT",  # CUIT
                    "documento_nro": invoice.customer_tax_id,
                    "razon_social": invoice.customer_name,
                    "email": "cliente@test.com",  # Required field
                    "domicilio": invoice.customer_address,
                    "condicion_iva": "RI",  # Responsable Inscripto
                    "condicion_pago": "Contado",  # Contado
                    "provincia": "1"  # Buenos Aires
                },
                "comprobante": {
                    "fecha": invoice.invoice_date.strftime("%d/%m/%Y"),
                    "tipo": "FACTURA A",
                    "operacion": "V",  # Venta
                    "punto_venta": "1",
                    "numero": "0",  # Will be assigned by the API
                    "periodo_facturado": {
                        "fecha_desde": invoice.invoice_date.strftime("%d/%m/%Y"),
                        "fecha_hasta": invoice.invoice_date.strftime("%d/%m/%Y")
                    },
                    "rubro": "Servicios",
                    "rubro_grupo_contable": "Servicios",
                    "detalle": self._prepare_items(invoice.items),
                    "moneda": {
                        "codigo": invoice.currency,
                        "cotizacion": "1"
                    }
                }
            }

            logger.info(f"Sending invoice data to TusFacturasApp: {invoice_data}")

            # Print the credentials
            logger.info(f"API URL: {self.api_url}")
            logger.info(f"API Key: {self.api_key}")
            logger.info(f"API Token: {self.api_token}")
            logger.info(f"User Token: {self.user_token}")

            # Send request to TusFacturasApp API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/nuevo",
                    json=invoice_data,
                    ssl=False  # Disable SSL verification for testing
                ) as response:
                    response_text = await response.text()
                    logger.info(f"TusFacturasApp API response status: {response.status}")
                    logger.info(f"TusFacturasApp API response headers: {response.headers}")
                    logger.info(f"TusFacturasApp API response body: {response_text}")

                    try:
                        result = await response.json()
                        logger.info(f"Parsed API response: {result}")

                        # Handle error responses
                        if response.status != 200:
                            error_msg = "Error en la conexión con la API"
                            if isinstance(result, dict):
                                error_msg = result.get("error_msg", error_msg)
                            raise Exception(f"TusFacturasApp error: {error_msg}")

                        # Handle API error responses
                        if isinstance(result, dict):
                            if result.get("error_response") == "S":
                                error_msg = result.get("error_msg", "Error desconocido")
                                raise Exception(f"TusFacturasApp error: {error_msg}")
                            elif result.get("error_response") == "N":
                                comprobante = result.get("comprobante", {})
                                return {
                                    "invoice_number": comprobante.get("numero"),
                                    "status": "success",
                                    "pdf_url": result.get("pdf_url"),
                                    "cae": result.get("cae"),
                                    "cae_vto": result.get("cae_vto"),
                                    "total": comprobante.get("total"),
                                    "tipo": comprobante.get("tipo"),
                                    "punto_venta": comprobante.get("punto_venta")
                                }

                        # Handle list responses
                        if isinstance(result, list) and len(result) > 0:
                            first_result = result[0]
                            if isinstance(first_result, dict):
                                if first_result.get("error_response") == "S":
                                    error_msg = first_result.get("error_msg", "Error desconocido")
                                    raise Exception(f"TusFacturasApp error: {error_msg}")
                                elif first_result.get("error_response") == "N":
                                    comprobante = first_result.get("comprobante", {})
                                    return {
                                        "invoice_number": comprobante.get("numero"),
                                        "status": "success",
                                        "pdf_url": first_result.get("pdf_url"),
                                        "cae": first_result.get("cae"),
                                        "cae_vto": first_result.get("cae_vto"),
                                        "total": comprobante.get("total"),
                                        "tipo": comprobante.get("tipo"),
                                        "punto_venta": comprobante.get("punto_venta")
                                    }

                        raise Exception(f"TusFacturasApp error: Formato de respuesta inesperado - {result}")

                    except Exception as e:
                        logger.error(f"Error processing API response: {e}")
                        raise

        except Exception as e:
            logger.error(f"Error generating invoice: {str(e)}")
            raise 