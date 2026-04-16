from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.users import get_current_user
from app.core.errors import forbidden
from app.db.session import get_db_session
from app.schemas.categories import CategoryCreate, CategoryRead
from app.schemas.orders import OrderRead, OrderStatusUpdate
from app.schemas.products import ProductCreate, ProductRead
from app.schemas.users import UserRead
from app.services.admin_orders import (
    get_admin_order,
    get_admin_orders,
    update_admin_order_status,
)
from app.services.catalog import create_category, create_product

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(current_user: UserRead = Depends(get_current_user)) -> UserRead:
    if not current_user.is_admin:
        raise forbidden("Admin access required")
    return current_user


@router.post("/categories", response_model=CategoryRead, status_code=201)
async def create_category_endpoint(
    payload: CategoryCreate,
    _: UserRead = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
) -> CategoryRead:
    return await create_category(session, payload)


@router.post("/products", response_model=ProductRead, status_code=201)
async def create_product_endpoint(
    payload: ProductCreate,
    admin_user: UserRead = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
) -> ProductRead:
    return await create_product(session, payload, admin_user.id)


@router.get("/orders", response_model=list[OrderRead])
async def read_admin_orders(
    _: UserRead = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
) -> list[OrderRead]:
    return await get_admin_orders(session)


@router.get("/orders/{order_id}", response_model=OrderRead)
async def read_admin_order(
    order_id: int,
    _: UserRead = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
) -> OrderRead:
    return await get_admin_order(session, order_id)


@router.patch("/orders/{order_id}/status", response_model=OrderRead)
async def update_admin_order_status_endpoint(
    order_id: int,
    payload: OrderStatusUpdate,
    _: UserRead = Depends(require_admin),
    session: AsyncSession = Depends(get_db_session),
) -> OrderRead:
    return await update_admin_order_status(
        session,
        order_id=order_id,
        new_status=payload.status,
    )
    