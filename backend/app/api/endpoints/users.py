from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import logger
from app.crud import crud_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserWithProfile,
    UserProfileUpdate,
    PasswordChange,
)

router = APIRouter()


async def get_current_user_from_session(
    request: Request, db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    user = await crud_user.get_user_by_id(db, user_id)
    if not user:
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


@router.get("/me", response_model=UserWithProfile)
async def read_users_me(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    current_user = await get_current_user_from_session(request, db)
    profile = await crud_user.get_user_profile(db, user_id=current_user.id)

    return UserWithProfile(user=current_user, profile=profile)


@router.put("/me/profile", response_model=UserWithProfile)
async def update_user_profile(
    request: Request,
    profile_update: UserProfileUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    current_user = await get_current_user_from_session(request, db)

    if not profile_update.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No update data provided"
        )

    updated_profile = await crud_user.update_user_profile(
        db, user_id=current_user.id, profile_in=profile_update
    )

    await db.refresh(current_user)

    logger.info(f"Profile updated for user {current_user.email}")
    return UserWithProfile(user=current_user, profile=updated_profile)


@router.post("/me/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    request: Request,
    password_change: PasswordChange,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    current_user = await get_current_user_from_session(request, db)

    if current_user.password_hash != password_change.old_password:
        logger.warning(f"Failed password change attempt for user {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password"
        )

    await crud_user.update_user_password(
        db, user_id=current_user.id, new_hash=password_change.new_password
    )

    logger.info(f"Password changed successfully for user {current_user.email}")
    return {"message": "Password updated successfully"}
