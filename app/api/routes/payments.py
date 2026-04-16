from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.users import get_current_user
from app.db.session import get_db_session
from app.schemas.payments import FakePaymentRequest, PaymentResultRead
from app.schemas.users import UserRead
from app.services.payments import get_order_payment_status, pay_order_with_fake_provider

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/orders/{order_id}/pay", response_model=PaymentResultRead)
async def pay_order(
    order_id: int,
    payload: FakePaymentRequest,
    current_user: UserRead = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> PaymentResultRead:
    return await pay_order_with_fake_provider(
        session,
        user_id=current_user.id,
        order_id=order_id,
        simulate_status=payload.simulate_status,
    )


@router.get("/orders/{order_id}", response_model=PaymentResultRead)
async def read_order_payment(
    order_id: int,
    current_user: UserRead = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> PaymentResultRead:
    return await get_order_payment_status(
        session,
        user_id=current_user.id,
        order_id=order_id,
    )