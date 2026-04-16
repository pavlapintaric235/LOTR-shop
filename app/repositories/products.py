from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.product import Product


async def list_products(
    session: AsyncSession,
    *,
    category_slug: str | None = None,
    featured: bool | None = None,
) -> list[Product]:
    query: Select[tuple[Product]] = (
        select(Product)
        .options(selectinload(Product.category))
        .order_by(Product.name.asc())
    )

    if category_slug is not None:
        query = query.join(Category).where(Category.slug == category_slug)

    if featured is not None:
        query = query.where(Product.is_featured == featured)

    result = await session.execute(query)
    return list(result.scalars().all())


async def get_product_by_id(session: AsyncSession, product_id: int) -> Product | None:
    query = (
        select(Product)
        .options(selectinload(Product.category))
        .where(Product.id == product_id)
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()

async def get_product_by_slug(session: AsyncSession, slug: str) -> Product | None:
    query = (
        select(Product)
        .options(selectinload(Product.category))
        .where(Product.slug == slug)
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()



async def get_featured_products(session: AsyncSession, limit: int = 8) -> list[Product]:
    query = (
        select(Product)
        .options(selectinload(Product.category))
        .where(Product.is_featured.is_(True))
        .order_by(Product.name.asc())
        .limit(limit)
    )
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_most_wanted_products(session: AsyncSession, limit: int = 8) -> list[Product]:
    query = (
        select(Product)
        .options(selectinload(Product.category))
        .order_by(Product.stock.asc(), Product.name.asc())
        .limit(limit)
    )
    result = await session.execute(query)
    return list(result.scalars().all())

async def create_product(
    session: AsyncSession,
    *,
    slug: str,
    name: str,
    description: str,
    price,
    stock: int,
    image_url: str,
    is_featured: bool,
    category_id: int,
    created_by_id: int | None,
) -> Product:
    product = Product(
        slug=slug,
        name=name,
        description=description,
        price=price,
        stock=stock,
        image_url=image_url,
        is_featured=is_featured,
        category_id=category_id,
        created_by_id=created_by_id,
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    refreshed = await get_product_by_id(session, product.id)
    assert refreshed is not None
    return refreshed


async def update_product(
    session: AsyncSession,
    *,
    product: Product,
    slug: str,
    name: str,
    description: str,
    price,
    stock: int,
    image_url: str,
    is_featured: bool,
    category_id: int,
) -> Product:
    product.slug = slug
    product.name = name
    product.description = description
    product.price = price
    product.stock = stock
    product.image_url = image_url
    product.is_featured = is_featured
    product.category_id = category_id

    await session.commit()
    await session.refresh(product)
    refreshed = await get_product_by_id(session, product.id)
    assert refreshed is not None
    return refreshed


async def delete_product(session: AsyncSession, product: Product) -> None:
    await session.delete(product)
    await session.commit()