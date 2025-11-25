from typing import Annotated
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.core.sessions import active_sessions
from app.models.user import User as UserModel


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: str = Header(..., alias="Authorization"),
) -> UserModel:
    try:
        scheme, param = token.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
            )
        token_str = param
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )

    if token_str not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    session_data = active_sessions[token_str]
    user_id = session_data.get("user_id")

    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
