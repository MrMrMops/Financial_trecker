
from app.schemas.auth_schema import UserCreate, UserOut, Token
from app.services.auth import get_current_user, register_user, login_user
from app.db.database import get_async_session
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter

from app.models.auth import User


auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def post_register_user(user: UserCreate, session: AsyncSession = Depends(get_async_session)):
    return await register_user(user,session)

@auth_router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def post_login_user(user: UserCreate, session: AsyncSession = Depends(get_async_session)):
    return await login_user(user,session)

@auth_router.get("/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user