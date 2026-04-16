from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.users import get_current_user
from app.db.session import get_db_session
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartRead
from app.schemas.users import UserRead
from app.services.cart import (
    add_item_to_cart,
    get_user_cart,
    remove_item_from_cart,
    update_item_in_cart,
)

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=CartRead)
async def read_cart(
    current_user: UserRead = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CartRead:
    return await get_user_cart(session, current_user.id)


@router.post("/items", response_model=CartRead)
async def add_cart_item_endpoint(
    payload: CartItemCreate,
    current_user: UserRead = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CartRead:
    return await add_item_to_cart(
        session,
        user_id=current_user.id,
        product_id=payload.product_id,
        quantity=payload.quantity,
    )


@router.put("/items/{item_id}", response_model=CartRead)
async def update_cart_item_endpoint(
    item_id: int,
    payload: CartItemUpdate,
    current_user: UserRead = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CartRead:
    return await update_item_in_cart(
        session,
        user_id=current_user.id,
        item_id=item_id,
        quantity=payload.quantity,
    )


@router.delete("/items/{item_id}", response_model=CartRead)
async def delete_cart_item_endpoint(
    item_id: int,
    current_user: UserRead = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> CartRead:
    return await remove_item_from_cart(
        session,
        user_id=current_user.id,
        item_id=item_id,
    )