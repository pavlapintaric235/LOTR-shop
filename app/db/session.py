
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine # type: ignore
from app.core.config import settings
from sqlalchemy.pool import NullPool # type: ignore

engine = create_async_engine(
    settings.database_url,
    echo=False,
    poolclass=NullPool,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session