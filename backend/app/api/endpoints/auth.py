from typing import Annotated
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import crud_user
from app.schemas.user import User, UserCreate, UserProfileCreate, UserRegister
from app.api.deps import get_current_user
from app.db.session import get_db
from app.core.logging_config import logger
from app.security.security import create_access_token, get_password_hash
from app.core.config import config


router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_register: UserRegister, db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Регистрирует нового пользователя в системе.
    """
    logger.info(f"Attempting to register user with email: {user_register.email}")
    db_user = await crud_user.get_user_by_email(db, email=user_register.email)

    if db_user:
        logger.warning(
            f"Registration failed: email {user_register.email} already registered."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    hashed_password = get_password_hash(user_register.plain_password)

    user_in_db = UserCreate(email=user_register.email, password_hash=hashed_password)

    new_user = await crud_user.create_user(db=db, user_in=user_in_db)
    logger.info(f"User {new_user.email} registered successfully with ID {new_user.id}")

    profile_in = UserProfileCreate(full_name=None, avatar_url=None, settings=None)
    await crud_user.create_user_profile(db, user_id=new_user.id, profile_in=profile_in)

    logger.info(f"Profile created for user ID: {new_user.id}")

    return new_user


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Аутентифицирует пользователя и возвращает JWT токен.
    Использует стандартный OAuth2 формат запроса (username=email, password=password).
    """
    logger.info(f"Authentication attempt for user: {form_data.username}")

    user = await crud_user.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )

    if not user:
        logger.warning(f"Authentication failed for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )

    logger.info(f"User {user.email} authenticated successfully. Token issued.")

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify-token")
async def verify_token(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Проверяет валидность токена и возвращает информацию о пользователе.
    """
    logger.info(f"Token verified for user: {current_user.email}")
    return current_user
