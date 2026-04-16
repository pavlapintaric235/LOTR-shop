from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


async def list_categories(session: AsyncSession) -> list[Category]:
    result = await session.execute(select(Category).order_by(Category.name.asc()))
    return list(result.scalars().all())

async def get_category_by_slug(session: AsyncSession, slug: str) -> Category | None:
    result = await session.execute(select(Category).where(Category.slug == slug))
    return result.scalar_one_or_none()


async def get_category_by_id(session: AsyncSession, category_id: int) -> Category | None:
    result = await session.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def create_category(
    session: AsyncSession,
    *,
    slug: str,
    name: str,
) -> Category:
    category = Category(slug=slug, name=name)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category