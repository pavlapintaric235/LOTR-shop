from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order
from app.models.order_item import OrderItem


async def create_order(
    session: AsyncSession,
    *,
    user_id: int,
    total_amount: Decimal,
    status: str = "pending",
    payment_status: str = "unpaid",
) -> Order:
    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        status=status,
        payment_status=payment_status,
    )
    session.add(order)
    await session.flush()
    return order


async def add_order_item(
    session: AsyncSession,
    *,
    order_id: int,
    product_id: int,
    product_name: str,
    unit_price: Decimal,
    quantity: int,
    subtotal: Decimal,
) -> OrderItem:
    item = OrderItem(
        order_id=order_id,
        product_id=product_id,
        product_name=product_name,
        unit_price=unit_price,
        quantity=quantity,
        subtotal=subtotal,
    )
    session.add(item)
    await session.flush()
    return item


async def list_orders_by_user_id(session: AsyncSession, user_id: int) -> list[Order]:
    query = (
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc(), Order.id.desc())
    )
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_order_by_id_and_user_id(
    session: AsyncSession,
    *,
    order_id: int,
    user_id: int,
) -> Order | None:
    query = (
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id, Order.user_id == user_id)
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def list_all_orders(session: AsyncSession) -> list[Order]:
    query = (
        select(Order)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc(), Order.id.desc())
    )
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_order_by_id(session: AsyncSession, order_id: int) -> Order | None:
    query = (
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def update_order_payment(
    session: AsyncSession,
    *,
    order: Order,
    payment_status: str,
    payment_provider: str | None,
    payment_reference: str | None,
    order_status: str,
) -> Order:
    order.payment_status = payment_status
    order.payment_provider = payment_provider
    order.payment_reference = payment_reference
    order.status = order_status
    await session.commit()
    await session.refresh(order)
    refreshed = await get_order_by_id_and_user_id(
        session,
        order_id=order.id,
        user_id=order.user_id,
    )
    assert refreshed is not None
    return refreshed


async def update_order_status(
    session: AsyncSession,
    *,
    order: Order,
    status: str,
) -> Order:
    order.status = status
    await session.commit()
    await session.refresh(order)
    refreshed = await get_order_by_id(session, order.id)
    assert refreshed is not None
    return refreshed