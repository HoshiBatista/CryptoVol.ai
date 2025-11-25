import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.crud import crud_user
from app.schemas.user import User, UserCreate, UserProfileCreate, UserRegister
from app.db.session import get_db
from app.core.sessions import active_sessions
from app.core.logging_config import logger

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_register: UserRegister, db: Annotated[AsyncSession, Depends(get_db)]
):
    logger.info(f"🔍 Starting registration for email: {user_register.email}")

    try:
        logger.debug("Checking if user exists...")
        existing_user = await crud_user.get_user_by_email(db, email=user_register.email)
        if existing_user:
            logger.warning(f"Email {user_register.email} already registered")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        logger.debug("Saving password without hashing...")
        plain_password = user_register.plain_password

        logger.debug("👤 Creating user record...")
        user_in_db = UserCreate(email=user_register.email, password_hash=plain_password)
        new_user = await crud_user.create_user(db=db, user_in=user_in_db)
        logger.info(f"Created user with ID: {new_user.id}")

        logger.debug("👤 Creating user profile...")
        profile_in = UserProfileCreate(full_name=None, avatar_url=None, settings=None)
        await crud_user.create_user_profile(
            db, user_id=new_user.id, profile_in=profile_in
        )
        logger.info(f"Created profile for user ID: {new_user.id}")

        logger.info(f"Registration completed successfully for {new_user.email}")

        return new_user

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Critical error during registration: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to internal error",
        )


@router.post("/login")
async def login_for_access_token(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    email: str = Form(...),
    password: str = Form(...),
):
    logger.info(f"Simple login attempt for user: {email}")

    try:
        user = await crud_user.get_user_by_email(db, email=email)

        if not user:
            logger.warning(f"Authentication failed for user: {email} - user not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        if user.password_hash != password:
            logger.warning(
                f"Authentication failed for user: {email} - incorrect password"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        token = str(uuid.uuid4())
        active_sessions[token] = {
            "user_id": str(user.id),
            "user_email": user.email,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=1),
        }

        logger.info(f"User {user.email} authenticated successfully. Token: {token}")
        return {"token": token, "email": user.email}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Critical error during login: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to internal error",
        )


@router.get("/logout")
async def logout(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token in active_sessions:
        del active_sessions[token]

    logger.info("User logged out")

    return {"message": "Logout successful"}
