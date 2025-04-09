import os
from zeep import Client
from zeep.transports import Transport
from zeep.exceptions import Fault
from ..models.invoice import InvoiceInputData
from datetime import datetime
import logging

class AFIPService:
    def __init__(self):
        self.certificate_path = os.getenv("AFIP_CERTIFICATE_PATH")
        self.private_key_path = os.getenv("AFIP_PRIVATE_KEY_PATH")
        self.cuit = os.getenv("AFIP_CUIT")
        self.environment = os.getenv("AFIP_ENVIRONMENT", "testing")  # testing or production
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize AFIP client
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the AFIP web service client"""
        try:
            # Load certificate and private key
            with open(self.certificate_path, 'rb') as cert_file:
                certificate = cert_file.read()
            
            with open(self.private_key_path, 'rb') as key_file:
                private_key = key_file.read()
            
            # Create transport with certificate
            transport = Transport(
                certificate=certificate,
                private_key=private_key
            )
            
            # Initialize client
            if self.environment == "testing":
                self.client = Client(
                    'https://servicios1.afip.gov.ar/wsfev1/service.asmx?wsdl',
                    transport=transport
                )
            else:
                self.client = Client(
                    'https://servicios1.afip.gov.ar/wsfev1/service.asmx?wsdl',
                    transport=transport
                )
                
        except Exception as e:
            self.logger.error(f"Failed to initialize AFIP client: {str(e)}")
            raise
    
    async def generate_invoice(self, invoice: InvoiceInputData) -> dict:
        """Generate an invoice using AFIP web service"""
        try:
            # Prepare invoice data
            invoice_data = {
                'CmpReq': {
                    'FeCabReq': {
                        'CantReg': 1,
                        'PuntoVenta': 1,
                        'Concepto': 1,
                        'DocTipo': 80,  # CUIT
                        'DocNro': invoice.customer_tax_id,
                        'Fecha': invoice.invoice_date.strftime('%Y%m%d'),
                        'ImpTotal': invoice.total_amount,
                        'ImpTotConc': 0,
                        'ImpNeto': invoice.total_amount - invoice.tax_amount,
                        'ImpOpEx': 0,
                        'ImpIVA': invoice.tax_amount,
                        'ImpTrib': 0,
                        'MonId': invoice.currency,
                        'MonCotiz': 1
                    },
                    'FeDetReq': {
                        'FECAEDet': [{
                            'Concepto': 1,
                            'DocTipo': 80,
                            'DocNro': invoice.customer_tax_id,
                            'CbteDesde': 0,  # Will be filled by AFIP
                            'CbteHasta': 0,  # Will be filled by AFIP
                            'CbteFch': invoice.invoice_date.strftime('%Y%m%d'),
                            'ImpTotal': invoice.total_amount,
                            'ImpTotConc': 0,
                            'ImpNeto': invoice.total_amount - invoice.tax_amount,
                            'ImpOpEx': 0,
                            'ImpIVA': invoice.tax_amount,
                            'ImpTrib': 0,
                            'MonId': invoice.currency,
                            'MonCotiz': 1,
                            'Iva': {
                                'AlicIva': [{
                                    'Id': 5,  # 21%
                                    'BaseImp': invoice.total_amount - invoice.tax_amount,
                                    'Importe': invoice.tax_amount
                                }]
                            }
                        }]
                    }
                }
            }
            
            # Call AFIP service
            response = self.client.service.FECAESolicitar(
                Auth={
                    'Token': self._get_token(),
                    'Sign': self._get_sign(),
                    'Cuit': self.cuit
                },
                CmpReq=invoice_data['CmpReq']
            )
            
            # Process response
            if response.Resultado == 'A':
                return {
                    'invoice_number': response.FeDetResp.FECAEDetResponse[0].CbteDesde,
                    'status': 'success'
                }
            else:
                raise Exception(f"AFIP error: {response.Errors.Err[0].Msg}")
                
        except Fault as e:
            self.logger.error(f"AFIP service error: {str(e)}")
            raise Exception(f"AFIP service error: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error generating invoice: {str(e)}")
            raise
    
    def _get_token(self) -> str:
        """Get authentication token from AFIP"""
        # Implementation depends on AFIP's authentication method
        # This is a placeholder
        return "token"
    
    def _get_sign(self) -> str:
        """Get signature for AFIP authentication"""
        # Implementation depends on AFIP's authentication method
        # This is a placeholder
        return "sign" 