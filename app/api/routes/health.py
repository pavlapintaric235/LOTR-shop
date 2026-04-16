from typing import Any

from fastapi import APIRouter, Depends # type: ignore
from sqlalchemy import text # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore

from app.db.session import get_db_session

router = APIRouter(tags=["health"])


@router.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/db")
async def db_healthcheck(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    result = await session.execute(text("SELECT 1"))
    return {"status": "ok", "db": result.scalar_one()}
