from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

if not settings.test_database_url:
    raise RuntimeError(
        "TEST_DATABASE_URL is missing or empty. "
        "Set TEST_DATABASE_URL in .env, for example: "
        "'postgresql+asyncpg://lotr_user:change_me@db:5432/lotr_shop_test'"
    )

test_engine = create_async_engine(
    settings.test_database_url,
    echo=False,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_test_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session