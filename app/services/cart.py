from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.repositories.cart import (
    add_cart_item,
    delete_cart_item,
    get_cart_item_by_cart_and_product,
    get_cart_item_by_id,
    get_or_create_cart,
    list_cart_items_by_user_id,
    update_cart_item_quantity,
)
from app.repositories.products import get_product_by_id
from app.schemas.cart import CartItemRead, CartRead
from app.schemas.products import ProductRead


def calculate_subtotal(product_price: Decimal, quantity: int) -> Decimal:
    return product_price * quantity


def calculate_total(items: list[CartItemRead]) -> Decimal:
    return sum((item.subtotal for item in items), start=Decimal("0.00"))


def to_cart_item_read(item: CartItem) -> CartItemRead:
    subtotal = calculate_subtotal(item.product.price, item.quantity)
    return CartItemRead(
        id=item.id,
        quantity=item.quantity,
        subtotal=subtotal,
        product=ProductRead.model_validate(item.product),
    )


async def build_cart_read_for_user(session: AsyncSession, user_id: int) -> CartRead:
    cart: Cart = await get_or_create_cart(session, user_id)
    raw_items = await list_cart_items_by_user_id(session, user_id)
    items = [to_cart_item_read(item) for item in raw_items]
    total = calculate_total(items)
    return CartRead(
        id=cart.id,
        items=items,
        total=total,
    )


async def get_user_cart(session: AsyncSession, user_id: int) -> CartRead:
    return await build_cart_read_for_user(session, user_id)


async def add_item_to_cart(
    session: AsyncSession,
    *,
    user_id: int,
    product_id: int,
    quantity: int,
) -> CartRead:
    product = await get_product_by_id(session, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    if quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested quantity exceeds available stock",
        )

    cart = await get_or_create_cart(session, user_id)

    existing_item = await get_cart_item_by_cart_and_product(
        session,
        cart_id=cart.id,
        product_id=product_id,
    )

    if existing_item is not None:
        new_quantity = existing_item.quantity + quantity
        if new_quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested quantity exceeds available stock",
            )
        await update_cart_item_quantity(
            session,
            item=existing_item,
            quantity=new_quantity,
        )
    else:
        await add_cart_item(
            session,
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
        )

    return await build_cart_read_for_user(session, user_id)


async def update_item_in_cart(
    session: AsyncSession,
    *,
    user_id: int,
    item_id: int,
    quantity: int,
) -> CartRead:
    item = await get_cart_item_by_id(session, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    cart = await get_or_create_cart(session, user_id)
    if item.cart_id != cart.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    product: Product = item.product
    if quantity > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested quantity exceeds available stock",
        )

    await update_cart_item_quantity(
        session,
        item=item,
        quantity=quantity,
    )
    return await build_cart_read_for_user(session, user_id)


async def remove_item_from_cart(
    session: AsyncSession,
    *,
    user_id: int,
    item_id: int,
) -> CartRead:
    item = await get_cart_item_by_id(session, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    cart = await get_or_create_cart(session, user_id)
    if item.cart_id != cart.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    await delete_cart_item(session, item)
    return await build_cart_read_for_user(session, user_id)