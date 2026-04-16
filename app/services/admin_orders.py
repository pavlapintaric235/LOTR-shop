from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import bad_request, not_found
from app.core.order_status import can_transition_order_status, is_valid_order_status
from app.repositories.orders import (
    get_order_by_id,
    list_all_orders,
    update_order_status,
)
from app.schemas.orders import OrderRead


def to_order_read_list(orders: list) -> list[OrderRead]:
    return [OrderRead.model_validate(order) for order in orders]


async def get_admin_orders(session: AsyncSession) -> list[OrderRead]:
    orders = await list_all_orders(session)
    return to_order_read_list(orders)


async def get_admin_order(session: AsyncSession, order_id: int) -> OrderRead:
    order = await get_order_by_id(session, order_id)
    if order is None:
        raise not_found("Order not found")
    return OrderRead.model_validate(order)


async def update_admin_order_status(
    session: AsyncSession,
    *,
    order_id: int,
    new_status: str,
) -> OrderRead:
    order = await get_order_by_id(session, order_id)
    if order is None:
        raise not_found("Order not found")

    if not is_valid_order_status(new_status):
        raise bad_request("Invalid order status")

    if not can_transition_order_status(order.status, new_status):
        raise bad_request(
            f"Cannot transition order from '{order.status}' to '{new_status}'"
        )

    updated_order = await update_order_status(
        session,
        order=order,
        status=new_status,
    )
    return OrderRead.model_validate(updated_order)