from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class InvoiceItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    tax_rate: float = 0.21  # Default IVA rate

class Invoice(BaseModel):
    customer_name: str
    customer_tax_id: str
    customer_address: str
    items: List[InvoiceItem]
    invoice_date: datetime = datetime.now()
    invoice_type: str = "A"  # Default to Type A invoice
    payment_method: str = "Transfer"
    currency: str = "ARS"
    
    @property
    def total_amount(self) -> float:
        # return sum(item.quantity * item.unit_price * (1 + item.tax_rate) for item in self.items)
        return sum(item.quantity * item.unit_price for item in self.items)

    @property
    def tax_amount(self) -> float:
        return sum(item.quantity * item.unit_price * item.tax_rate for item in self.items) 