from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

# --- Enums based on documentation ---

class DocumentoTipo(str, Enum):
    CUIT = "CUIT"
    DNI = "DNI"
    PASAPORTE = "PASAPORTE"
    OTRO = "OTRO"

class EnviaPorMailOption(str, Enum):
    S = "S"  # Yes
    N = "N"  # No

class ConditionIVA(str, Enum):
    RI = "RI"  # Responsable Inscripto
    CF = "CF"  # Consumidor Final
    M = "M"    # Monotributista
    E = "E"    # Exento

# Note: This corresponds to 'condicion_iva_operacion' which becomes required from 15/04/2025
class ConditionIVAOperacion(str, Enum):
    RI = "RI"
    CF = "CF"
    # Add other values if needed based on RG 5616/2024

class RG5329Option(str, Enum):
    S = "S" # Subject to perception
    N = "N" # Not subject to perception

class ReclamaDeudaOption(str, Enum):
    S = "S" # Yes
    N = "N" # No

# --- Existing Enums (Potentially for internal use or other APIs) ---

class InvoiceType(str, Enum):
    A = "FACTURA A"
    B = "FACTURA B"
    C = "FACTURA C"
    E = "FACTURA E"

class PaymentMethod(str, Enum):
    TRANSFER = "Transfer"
    CASH = "Cash"
    CREDIT_CARD = "Credit Card"
    DEBIT_CARD = "Debit Card"
    CHECK = "Check"
    MERCADO_PAGO = "Mercado Pago"

class Currency(str, Enum):
    ARS = "ARS"
    USD = "USD"
    EUR = "EUR"

# --- Model Definitions ---

class InvoiceItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    tax_rate: float = 0.21  # Default IVA rate

class InvoiceInputData(BaseModel):
    # --- Required Fields based on Documentation ---
    documento_tipo: DocumentoTipo = Field(default=DocumentoTipo.CUIT, description="Tipo de documento del cliente. En caso de no especificar cliente, debe ser OTRO.")
    documento_nro: str = Field(..., description="Campo numérico, sin puntos ni guiones. En caso de no especificar cliente, debe ser '0'")
    razon_social: str = Field(..., max_length=255, description="Customer's full name or company name.")
    domicilio: str = Field(..., max_length=255, description="Customer's address.")
    provincia: int = Field(..., description="Código numérico de provincia según tabla de referencia(*).") # Needs table lookup
    envia_por_mail: EnviaPorMailOption
    condicion_pago: int = Field(..., description="Código numérico según tabla de referencia(*).") # Needs table lookup
    condicion_iva: ConditionIVA
    codigo: str = Field(..., max_length=50, description="Customer reference code, should be unique.")
    rg5329: RG5329Option

    # --- Optional Fields based on Documentation ---
    email: Optional[str] = Field(None, max_length=255, description="Máximo 15 direcciones separadas por coma.")
    condicion_pago_otra: Optional[str] = Field(None, max_length=100, description="Required if condicion_pago is 'Otra' (214).")
    condicion_iva_operacion: Optional[ConditionIVAOperacion] = Field(None, description="Required from 15/04/2025 (RG 5616/2024). Defaults to condicion_iva if not sent.")
    reclama_deuda: Optional[ReclamaDeudaOption] = None
    reclama_deuda_dias: Optional[int] = None
    reclama_deuda_repite_dias: Optional[int] = None

    # --- Existing Fields (Review if still needed in this specific model) ---
    items: List[InvoiceItem] # Assuming items are part of the input needed
    customer_name: str # Redundant? razon_social seems the correct field name for the API. Consider removing.
    customer_tax_id: str # Redundant? documento_nro seems the correct field name for the API. Consider removing.
    customer_address: str # Redundant? domicilio seems the correct field name for the API. Consider removing.
    customer_email: Optional[str] = None # Redundant? email field exists. Consider removing.

    invoice_date: datetime = Field(default_factory=datetime.now)
    invoice_type: InvoiceType = Field(description="Tipo de factura.") # May be needed for API call structure, check tusfacturas_service
    payment_method: PaymentMethod = Field(description="Método de pago.") # May be needed internally, but API uses condicion_pago code. Review usage.
    currency: Currency = Field(default=Currency.ARS, description="Moneda de la factura.") # May be needed for API call structure, check tusfacturas_service

    # --- Properties (Recalculate based on items) ---
    @property
    def total_amount(self) -> float:
        return sum(item.quantity * item.unit_price for item in self.items)

    @property
    def tax_amount(self) -> float:
        return sum(item.quantity * item.unit_price * item.tax_rate for item in self.items)

    # Consider adding model validation (validators) if needed, e.g., for documento_nro format. 