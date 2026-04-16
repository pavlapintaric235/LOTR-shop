from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db_session
from app.services.seed import reset_database_state, seed_test_data

router = APIRouter(prefix="/testing", tags=["testing"])


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_and_seed(
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    if not settings.testing_routes_enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found",
        )

    await reset_database_state(session)
    await seed_test_data(session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)