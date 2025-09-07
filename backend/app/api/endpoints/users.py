from typing import Annotated
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import User as UserSchema

router = APIRouter()


@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Возвращает данные о текущем аутентифицированном пользователе.

    Доступ к этому эндпоинту возможен только при наличии валидного
    JWT токена в заголовке Authorization.
    """
    return current_user
