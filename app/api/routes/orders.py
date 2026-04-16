from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.users import get_current_user
from app.db.session import get_db_session
from app.schemas.orders import OrderRead
from app.schemas.users import UserRead
from app.services.orders import checkout_cart, get_user_order, get_user_orders

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/checkout", response_model=OrderRead)
async def checkout_order(
    current_user: UserRead = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> OrderRead:
    return await checkout_cart(session, current_user.id)


@router.get("", response_model=list[OrderRead])
async def read_orders(
    current_user: UserRead = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[OrderRead]:
    return await get_user_orders(session, current_user.id)


@router.get("/{order_id}", response_model=OrderRead)
async def read_order(
    order_id: int,
    current_user: UserRead = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> OrderRead:
    return await get_user_order(
        session,
        user_id=current_user.id,
        order_id=order_id,
    )