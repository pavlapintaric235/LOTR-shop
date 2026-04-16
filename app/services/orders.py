from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import bad_request, not_found
from app.models.order import Order
from app.repositories.cart import get_or_create_cart, list_cart_items_by_user_id
from app.repositories.orders import (
    add_order_item,
    create_order,
    get_order_by_id_and_user_id,
    list_orders_by_user_id,
)
from app.schemas.orders import OrderRead


def to_order_read(order: Order) -> OrderRead:
    return OrderRead.model_validate(order)


async def checkout_cart(session: AsyncSession, user_id: int) -> OrderRead:
    await get_or_create_cart(session, user_id)
    cart_items = await list_cart_items_by_user_id(session, user_id)

    if not cart_items:
        raise bad_request("Cart is empty")

    total_amount = Decimal("0.00")

    for item in cart_items:
        if item.quantity > item.product.stock:
            raise bad_request(
                f"Insufficient stock for product '{item.product.name}'"
            )
        total_amount += item.product.price * item.quantity

    order = await create_order(
        session,
        user_id=user_id,
        total_amount=total_amount,
        status="pending",
        payment_status="unpaid",
    )

    for item in cart_items:
        subtotal = item.product.price * item.quantity

        await add_order_item(
            session,
            order_id=order.id,
            product_id=item.product.id,
            product_name=item.product.name,
            unit_price=item.product.price,
            quantity=item.quantity,
            subtotal=subtotal,
        )

        item.product.stock -= item.quantity
        await session.delete(item)

    await session.commit()

    refreshed_order = await get_order_by_id_and_user_id(
        session,
        order_id=order.id,
        user_id=user_id,
    )
    assert refreshed_order is not None
    return to_order_read(refreshed_order)


async def get_user_orders(session: AsyncSession, user_id: int) -> list[OrderRead]:
    orders = await list_orders_by_user_id(session, user_id)
    return [to_order_read(order) for order in orders]


async def get_user_order(
    session: AsyncSession,
    *,
    user_id: int,
    order_id: int,
) -> OrderRead:
    order = await get_order_by_id_and_user_id(
        session,
        order_id=order_id,
        user_id=user_id,
    )
    if order is None:
        raise not_found("Order not found")
    return to_order_read(order)