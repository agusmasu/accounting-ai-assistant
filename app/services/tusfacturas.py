import os
import logging
from typing import Dict, Any, List, Optional
import aiohttp
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app.models.invoice import InvoiceInputData, InvoiceItem
import requests

from app.models.user import User
from app.services.user import UserService
from app.services.context import ContextService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TusFacturasService:
    def __init__(self, user_service: UserService):
        """Initialize TusFacturasApp service with API credentials"""
        load_dotenv()
        self.api_url = "https://www.tusfacturas.app/app/api/v2/facturacion"
        self.api_key = os.getenv("TUSFACTURAS_API_KEY")
        self.api_token = os.getenv("TUSFACTURAS_API_TOKEN")
        self.user_token = os.getenv("TUSFACTURAS_USER_TOKEN")

        if not all([self.api_key, self.api_token, self.user_token]):
            raise ValueError("Missing required TusFacturasApp credentials in environment variables")

        self.user_service = user_service

    def _prepare_items(self, items: List[InvoiceItem]) -> List[Dict[str, Any]]:
        """Prepare invoice items in TusFacturasApp format"""
        formatted_items = []
        for item in items:
            formatted_item = {
                "cantidad": str(item.quantity),
                "producto": {
                    "descripcion": item.description,
                    "unidad_bulto": "1",
                    # "lista_precios": "Lista de precios API 3",
                    "codigo": "001",
                    "precio_unitario_sin_iva": str(item.unit_price),
                    "alicuota": "0"  # 0% for Factura C
                },
                "leyenda": ""
            }
            formatted_items.append(formatted_item)
        return formatted_items

    async def generate_invoice(self, invoice: InvoiceInputData, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate an invoice using TusFacturasApp API
        
        Args:
            invoice: The invoice data
            user_id: Optional user ID (will use from context if not provided)
            
        Returns:
            The generated invoice data
        """
        try:
            # Get the user (either from user_id parameter or from context)
            user: Optional[User] = None
            
            if user_id:
                # If user_id is provided, use it
                user = self.user_service.get_user_by_id(user_id)
            else:
                # Otherwise try to get from context
                user = ContextService.get_current_user()
                
            if not user:
                raise Exception("User not found - neither provided as parameter nor available in context")

            # Calculate expiration date (30 days from invoice date)
            expiration_date = invoice.invoice_date + timedelta(days=30)

            logger.info(f"Creating invoice for user: {user.name}")

            # Prepare invoice data according to TusFacturasApp format
            invoice_data = {
                "usertoken": user.user_token,
                "apikey": self.api_key,
                "apitoken": self.api_token,
                "cliente": {
                    "documento_tipo": invoice.documento_tipo,
                    "documento_nro": invoice.customer_tax_id,
                    "razon_social": invoice.customer_name,
                    "email": invoice.customer_email,
                    "domicilio": invoice.customer_address,
                    "provincia": "1",
                    "reclama_deuda": "N",
                    "envia_por_mail": "N",
                    "condicion_pago": "Contado",
                    "condicion_iva": invoice.condicion_iva,
                    "condicion_iva_operacion": invoice.condicion_iva_operacion
                },
                "comprobante": {
                    "fecha": invoice.invoice_date.strftime("%d/%m/%Y"),
                    "vencimiento": expiration_date.strftime("%d/%m/%Y"),
                    "tipo": invoice.invoice_type,
                    "external_reference": f"{invoice.invoice_date.strftime('%m%y')}-{invoice.invoice_date.strftime('%m%y')}",
                    "tags": ["FacturAI"],
                    "datos_informativos": {
                        "paga_misma_moneda": "N"
                    },
                    "operacion": "V",
                    "punto_venta": "0001",
                    "moneda": invoice.currency,
                    "cotizacion": 1,
                    "periodo_facturado_desde": invoice.invoice_date.strftime("%d/%m/%Y"),
                    "periodo_facturado_hasta": invoice.invoice_date.strftime("%d/%m/%Y"),
                    "rubro": "Servicios",
                    "rubro_grupo_contable": "Servicios",
                    "detalle": self._prepare_items(invoice.items),
                    "bonificacion": "0.00",
                    "leyenda_gral": " ",
                    "total": str(invoice.total_amount),
                    "pagos": {
                        "formas_pago": [
                            {
                                "descripcion": invoice.payment_method,
                                "importe": invoice.total_amount
                            }
                        ],
                        "total": invoice.total_amount
                    }
                }
            }

            logger.info(f"Sending invoice data to TusFacturasApp: {invoice_data}")

            # Send request to TusFacturasApp API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/nuevo",
                    json=invoice_data,
                    ssl=False  # Disable SSL verification for testing
                ) as response:
                    response_text = await response.text()
                    logger.info(f"TusFacturasApp API response status: {response.status}")
                    logger.info(f"TusFacturasApp API response body: {response_text}")

                    try:
                        result = await response.json()
                        logger.info(f"Parsed API response: {result}")

                        # Handle error responses
                        if response.status != 200:
                            error_msg = "Error en la conexión con la API"
                            if isinstance(result, dict):
                                error_msg = result.get("error_msg", error_msg)
                            logger.error(f"TusFacturasApp error: {error_msg}")
                            raise Exception(f"TusFacturasApp error: {error_msg}")

                        # Handle API error responses
                        if isinstance(result, dict):
                            if result.get("error") == "S":
                                # Format error messages from error_details if available
                                error_messages = []
                                if result.get("error_details"):
                                    error_messages.extend([detail["text"] for detail in result["error_details"]])
                                if result.get("errores"):
                                    error_messages.extend(result["errores"])
                                
                                error_msg = " | ".join(error_messages) if error_messages else "Error desconocido"
                                logger.error(f"TusFacturasApp error: {error_msg}")
                                raise Exception(f"TusFacturasApp error: {error_msg}")
                            elif result.get("error") == "N":
                                return {
                                    "invoice_number": result.get("comprobante_nro"),
                                    "status": "success",
                                    "pdf_url": result.get("comprobante_pdf_url"),
                                    "cae": result.get("cae"),
                                    "cae_vto": result.get("vencimiento_cae"),
                                    "total": invoice.total_amount,
                                    "tipo": result.get("comprobante_tipo"),
                                    "punto_venta": result.get("comprobante_nro", "").split("-")[0],
                                    "external_reference": result.get("external_reference"),
                                    "observaciones": result.get("observaciones"),
                                    "afip_qr": result.get("afip_qr"),
                                    "afip_codigo_barras": result.get("afip_codigo_barras")
                                }
                        logger.error(f"TusFacturasApp error: Formato de respuesta inesperado - {result}")
                        raise Exception(f"TusFacturasApp error: Formato de respuesta inesperado - {result}")

                    except Exception as e:
                        logger.error(f"Error processing API response: {e}")
                        raise

        except Exception as e:
            logger.error(f"Error generating invoice: {str(e)}")
            raise 