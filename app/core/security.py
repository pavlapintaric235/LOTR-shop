from datetime import datetime, timedelta, timezone

import jwt # type: ignore
from passlib.context import CryptContext # type: ignore

from app.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
       minutes=settings.access_token_expire_minutes
)
    payload = {
       "sub": subject,
       "exp": expire,
}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
