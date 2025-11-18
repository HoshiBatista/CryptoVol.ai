from typing import Optional
from fastapi import HTTPException
from sqlalchemy import UUID
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserProfile, Role, UserRole
from app.core.logging_config import logger
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserProfileCreate,
    UserProfileUpdate,
)


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    logger.info(f"Fetching user by email: {email}")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if user:
        logger.info(f"User found: {user.id}")
    else:
        logger.info(f"User with email {email} not found")

    return user


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    logger.info(f"Creating user with email: {user_in.email}")

    db_user = User(
        email=user_in.email,
        password_hash=user_in.password_hash,
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    logger.info(f"User created successfully with ID: {db_user.id}")

    return db_user


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    logger.info(f"Fetching user by ID: {user_id}")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if user:
        logger.info(f"User found: {user.id}")
    else:
        logger.info(f"User with ID {user_id} not found")

    return user


async def update_user(
    db: AsyncSession, user_id: str, user_update: UserUpdate
) -> Optional[User]:
    logger.info(f"Updating user with ID: {user_id}")

    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()

    if not db_user:
        logger.warning(f"Attempt to update non-existent user ID: {user_id}")
        return None

    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, key, value)

    await db.commit()
    await db.refresh(db_user)

    logger.info(f"User ID {user_id} updated successfully")

    return db_user


async def get_user_profile(db: AsyncSession, user_id: str) -> Optional[UserProfile]:
    logger.info(f"Fetching profile for user ID: {user_id}")

    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.scalars().first()

    if profile:
        logger.info(f"Profile found for user ID: {user_id}")
    else:
        logger.info(f"Profile for user ID {user_id} not found")

    return profile


async def create_user_profile(
    db: AsyncSession, user_id: UUID, profile_in: UserProfileCreate
) -> UserProfile:
    logger.debug(f"Creating profile for user ID: {user_id}")

    profile_data = profile_in.model_dump(exclude_unset=True)

    db_profile = UserProfile(
        user_id=user_id,
        full_name=profile_data.get("full_name"),
        avatar_url=profile_data.get("avatar_url"),
        settings=profile_data.get("settings"),
    )

    db.add(db_profile)
    try:
        await db.commit()
        await db.refresh(db_profile)
        logger.info(f"Created profile for user ID: {user_id}")

        return db_profile

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create profile: {str(e)}")
        raise


async def update_user_profile(
    db: AsyncSession, user_id: UUID, profile_in: UserProfileUpdate
) -> UserProfile:
    profile = await get_user_profile(db, user_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    update_data = profile_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(profile, field, value)

    try:
        await db.commit()
        await db.refresh(profile)
        return profile
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update profile: {str(e)}")
        raise


async def get_role_by_name(db: AsyncSession, name: str) -> Optional[Role]:
    logger.info(f"Fetching role by name: {name}")

    result = await db.execute(select(Role).where(Role.name == name))
    role = result.scalars().first()

    if role:
        logger.info(f"Role found: {role.id}")
    else:
        logger.info(f"Role with name {name} not found")

    return role


async def update_user_password(
    db: AsyncSession, user_id: UUID, hashed_password: str
) -> None:
    user = await get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hashed_password

    await db.commit()


async def assign_role_to_user(db: AsyncSession, user_id: str, role_id: int) -> bool:
    logger.info(f"Assigning role ID {role_id} to user ID {user_id}")

    result = await db.execute(
        select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
    )

    existing = result.scalars().first()

    if existing:
        logger.warning(f"Role ID {role_id} already assigned to user ID {user_id}")
        return False

    new_role = UserRole(user_id=user_id, role_id=role_id)
    db.add(new_role)
    await db.commit()

    logger.info(f"Role ID {role_id} assigned to user ID {user_id} successfully")

    return True
