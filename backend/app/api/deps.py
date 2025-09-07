from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.security.security import ALGORITHM, SECRET_KEY
from app.crud import crud_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import TokenData


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Декодирует JWT токен, валидирует его и возвращает объект пользователя из БД.
    Это наша главная зависимость для защиты эндпоинтов.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception

        token_data = TokenData(email=email)
    except (JWTError, ValidationError):
        raise credentials_exception

    user = await crud_user.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception

    return user
