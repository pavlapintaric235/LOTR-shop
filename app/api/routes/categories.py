from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.categories import list_categories
from app.schemas.categories import CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryRead])
async def read_categories(
    session: AsyncSession = Depends(get_db_session),
) -> list[CategoryRead]:
    categories = await list_categories(session)
    return [CategoryRead.model_validate(category) for category in categories]