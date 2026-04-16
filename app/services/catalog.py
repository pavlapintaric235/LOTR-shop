from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import bad_request, not_found
from app.models.category import Category
from app.models.product import Product
from app.schemas.categories import CategoryCreate, CategoryRead
from app.schemas.products import ProductCreate, ProductRead


async def create_category(
    session: AsyncSession,
    payload: CategoryCreate,
) -> CategoryRead:
    existing_category = await session.execute(
        select(Category).where(Category.slug == payload.slug)
    )
    if existing_category.scalar_one_or_none() is not None:
        raise bad_request("Category with this slug already exists")

    category = Category(
        name=payload.name,
        slug=payload.slug,
    )
    session.add(category)
    await session.commit()
    await session.refresh(category)

    return CategoryRead.model_validate(category)


async def create_product(
    session: AsyncSession,
    payload: ProductCreate,
    created_by_id: int,
) -> ProductRead:
    existing_product = await session.execute(
        select(Product).where(Product.slug == payload.slug)
    )
    if existing_product.scalar_one_or_none() is not None:
        raise bad_request("Product with this slug already exists")

    category = await session.get(Category, payload.category_id)
    if category is None:
        raise not_found("Category not found")

    product = Product(
        name=payload.name,
        slug=payload.slug,
        description=payload.description,
        price=payload.price,
        stock=payload.stock,
        image_url=payload.image_url,
        is_featured=payload.is_featured,
        category_id=payload.category_id,
        created_by_id=created_by_id,
    )
    session.add(product)
    await session.commit()

    result = await session.execute(
        select(Product)
        .options(selectinload(Product.category))
        .where(Product.id == product.id)
    )
    created_product = result.scalar_one()

    return ProductRead.model_validate(created_product)