import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import bad_request, not_found
from app.repositories.orders import get_order_by_id_and_user_id, update_order_payment
from app.schemas.payments import PaymentResultRead

VALID_FAKE_STATUSES = {"success", "failed"}


async def pay_order_with_fake_provider(
    session: AsyncSession,
    *,
    user_id: int,
    order_id: int,
    simulate_status: str,
) -> PaymentResultRead:
    order = await get_order_by_id_and_user_id(
        session,
        order_id=order_id,
        user_id=user_id,
    )
    if order is None:
        raise not_found("Order not found")

    if simulate_status not in VALID_FAKE_STATUSES:
        raise bad_request("simulate_status must be either 'success' or 'failed'")

    if order.payment_status == "paid":
        raise bad_request("Order is already paid")

    if order.status in {"cancelled", "delivered"}:
        raise bad_request("Order can no longer be paid")

    payment_reference = f"fakepay_{uuid.uuid4().hex[:12]}"

    if simulate_status == "success":
        updated_order = await update_order_payment(
            session,
            order=order,
            payment_status="paid",
            payment_provider="fakepay",
            payment_reference=payment_reference,
            order_status="confirmed",
        )
    else:
        updated_order = await update_order_payment(
            session,
            order=order,
            payment_status="failed",
            payment_provider="fakepay",
            payment_reference=payment_reference,
            order_status="payment_failed",
        )

    return PaymentResultRead(
        order_id=updated_order.id,
        payment_status=updated_order.payment_status,
        payment_provider=updated_order.payment_provider,
        payment_reference=updated_order.payment_reference,
        order_status=updated_order.status,
    )


async def get_order_payment_status(
    session: AsyncSession,
    *,
    user_id: int,
    order_id: int,
) -> PaymentResultRead:
    order = await get_order_by_id_and_user_id(
        session,
        order_id=order_id,
        user_id=user_id,
    )
    if order is None:
        raise not_found("Order not found")

    return PaymentResultRead(
        order_id=order.id,
        payment_status=order.payment_status,
        payment_provider=order.payment_provider,
        payment_reference=order.payment_reference,
        order_status=order.status,
    )