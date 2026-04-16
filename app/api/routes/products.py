from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.products import (
    get_featured_products,
    get_most_wanted_products,
    get_product_by_id,
    list_products,
)
from app.schemas.products import HomepageRead, ProductRead

router = APIRouter(tags=["products"])


@router.get("/products", response_model=list[ProductRead])
async def read_products(
    category: str | None = Query(default=None),
    featured: bool | None = Query(default=None),
    session: AsyncSession = Depends(get_db_session),
) -> list[ProductRead]:
    products = await list_products(
        session,
        category_slug=category,
        featured=featured,
    )
    return [ProductRead.model_validate(product) for product in products]


@router.get("/products/{product_id}", response_model=ProductRead)
async def read_product(
    product_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> ProductRead:
    product = await get_product_by_id(session, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return ProductRead.model_validate(product)


@router.get("/homepage", response_model=HomepageRead)
async def read_homepage(
    session: AsyncSession = Depends(get_db_session),
) -> HomepageRead:
    featured_products = await get_featured_products(session)
    most_wanted_products = await get_most_wanted_products(session)
    return HomepageRead(
        featured_products=[ProductRead.model_validate(product) for product in featured_products],
        most_wanted_products=[ProductRead.model_validate(product) for product in most_wanted_products],
    )