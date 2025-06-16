from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.models.auth import User
from app.schemas.auth_schema import UserCreate, UserOut, Token
from app.services.auth import register_user, login_user, get_current_user

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
    description="Регистрирует нового пользователя и возвращает его данные без пароля."
)
async def register_user_route(
    user_create: UserCreate,
    session: AsyncSession = Depends(get_async_session)
) -> UserOut:
    """Регистрирует нового пользователя и возвращает UserOut."""
    return await register_user(user_create, session)


@auth_router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Аутентификация пользователя",
    description="Принимает имя и пароль, возвращает JWT токен при успешной аутентификации."
)
async def login_user_route(
    user_credentials: UserCreate,
    session: AsyncSession = Depends(get_async_session)
) -> Token:
    """Аутентифицирует пользователя и возвращает токен."""
    return await login_user(user_credentials, session)


@auth_router.get(
    "/me",
    response_model=UserOut,
    summary="Информация о текущем пользователе",
    description="Возвращает данные текущего аутентифицированного пользователя."
)
async def get_current_user_route(
    current_user: User = Depends(get_current_user)
) -> User:
    """Возвращает текущего пользователя на основании JWT токена."""
    return current_user
