from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_db_session
from app.repositories.users import (
    create_user,
    get_user_by_email,
    get_user_by_username,
)
from app.schemas.auth import Token
from app.schemas.users import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_db_session),
) -> UserRead:
    existing_email = await get_user_by_email(session, payload.email)
    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    existing_username = await get_user_by_username(session, payload.username)
    if existing_username is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    user = await create_user(
        session,
        email=payload.email,
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
    )
    return UserRead.model_validate(user)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session),
) -> Token:
    user = await get_user_by_username(session, form_data.username)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.username)
    return Token(access_token=access_token, token_type="bearer")