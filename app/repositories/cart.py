from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product


async def get_cart_by_user_id(session: AsyncSession, user_id: int) -> Cart | None:
    query = (
        select(Cart)
        .where(Cart.user_id == user_id)
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def create_cart(session: AsyncSession, user_id: int) -> Cart:
    cart = Cart(user_id=user_id)
    session.add(cart)
    await session.flush()
    await session.commit()
    await session.refresh(cart)
    return cart


async def get_or_create_cart(session: AsyncSession, user_id: int) -> Cart:
    cart = await get_cart_by_user_id(session, user_id)
    if cart is not None:
        return cart
    return await create_cart(session, user_id)


async def list_cart_items_by_user_id(session: AsyncSession, user_id: int) -> list[CartItem]:
    query = (
        select(CartItem)
        .join(Cart, Cart.id == CartItem.cart_id)
        .options(
            selectinload(CartItem.product).selectinload(Product.category)
        )
        .where(Cart.user_id == user_id)
        .order_by(CartItem.id.asc())
    )
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_cart_item_by_id(session: AsyncSession, item_id: int) -> CartItem | None:
    query = (
        select(CartItem)
        .options(
            selectinload(CartItem.product).selectinload(Product.category)
        )
        .where(CartItem.id == item_id)
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_cart_item_by_cart_and_product(
    session: AsyncSession,
    *,
    cart_id: int,
    product_id: int,
) -> CartItem | None:
    query = (
        select(CartItem)
        .options(
            selectinload(CartItem.product).selectinload(Product.category)
        )
        .where(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id,
        )
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def add_cart_item(
    session: AsyncSession,
    *,
    cart_id: int,
    product_id: int,
    quantity: int,
) -> CartItem:
    item = CartItem(
        cart_id=cart_id,
        product_id=product_id,
        quantity=quantity,
    )
    session.add(item)
    await session.flush()
    await session.commit()
    refreshed = await get_cart_item_by_id(session, item.id)
    assert refreshed is not None
    return refreshed


async def update_cart_item_quantity(
    session: AsyncSession,
    *,
    item: CartItem,
    quantity: int,
) -> CartItem:
    item.quantity = quantity
    await session.flush()
    await session.commit()
    refreshed = await get_cart_item_by_id(session, item.id)
    assert refreshed is not None
    return refreshed


async def delete_cart_item(session: AsyncSession, item: CartItem) -> None:
    await session.delete(item)
    await session.flush()
    await session.commit()