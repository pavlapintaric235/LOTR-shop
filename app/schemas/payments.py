from pydantic import BaseModel


class FakePaymentRequest(BaseModel):
    simulate_status: str = "success"


class PaymentResultRead(BaseModel):
    order_id: int
    payment_status: str
    payment_provider: str | None
    payment_reference: str | None
    order_status: str