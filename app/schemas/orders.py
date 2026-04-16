from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OrderItemRead(BaseModel):
    id: int
    product_id: int
    product_name: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal

    model_config = {"from_attributes": True}


class OrderRead(BaseModel):
    id: int
    status: str
    payment_status: str
    payment_provider: str | None
    payment_reference: str | None
    total_amount: Decimal
    created_at: datetime
    items: list[OrderItemRead]

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: str