from typing import List
from fastapi import APIRouter, Path, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import User
from app.schemas.category_schema import CategoryBase,CategoryOut
from app.services.auth import get_current_user
from app.db.database import get_async_session
from app.services.category import (
    create_category,
    delete_category,
    get_all_category,
    get_one_category,
    update_category,
)

categories_router = APIRouter(prefix="/categories", tags=["categories"])

@categories_router.post(
    '/',
    # response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создание категории",
    description="Создает новую категорию для текущего пользователя. Требуется только название категории."
)
async def create_category_route(
        category: CategoryBase,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)):
    return await create_category(category=category, user=user, session=session)


@categories_router.patch(
    '/{category_id}',
    response_model=CategoryBase,
    summary="Обновление категории",
    description="Обновляет существующую категорию по ID. Только владелец может её изменить."
)
async def update_category_route(
        category: CategoryBase,
        category_id: int = Path(..., ge=1),
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)):
    return await update_category(category, user, session, category_id)


@categories_router.delete(
    '/{category_id}',
    status_code=status.HTTP_200_OK,
    summary="Удаление категории",
    description="Удаляет категорию по ID. Доступно только владельцу."
)
async def delete_category_route(
        category_id: int = Path(..., ge=1),
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)):
    return await delete_category(user=user, session=session, category_id=category_id)


@categories_router.get(
    '/{category_id}',
    response_model=CategoryOut,
    summary="Получить одну категорию",
    description="Возвращает данные конкретной категории по её ID. Доступно только владельцу."
)
async def get_category_route(
        category_id: int = Path(..., ge=1),
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)):
    return await get_one_category(user=user, session=session, category_id=category_id)


@categories_router.get(
    '/',
    response_model=List[CategoryOut],
    summary="Получить все категории",
    description="Возвращает список всех категорий, созданных текущим пользователем."
)
async def get_all_categories_route(
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)):
    return await get_all_category(user=user, session=session)