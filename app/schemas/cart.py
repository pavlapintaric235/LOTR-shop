from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.products import ProductRead


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartItemRead(BaseModel):
    id: int
    quantity: int
    subtotal: Decimal
    product: ProductRead

    model_config = {"from_attributes": True}


class CartRead(BaseModel):
    id: int
    items: list[CartItemRead]
    total: Decimal