from typing import Any
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt

from app.core.config import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = config.ALGORITHM
SECRET_KEY = config.SECRET_KEY.get_secret_value()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, соответствует ли пароль хешу."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Создает хеш из пароля."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str | Any, expires_delta: timedelta | None = None
) -> str:
    """Создает новый JWT токен доступа."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
