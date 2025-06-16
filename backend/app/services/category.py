import logging
from typing import List

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import get_async_session
from app.models.auth import User
from app.models.transactions import Category
from app.schemas.category_schema import CategoryBase, CategoryOut
from app.services.auth import get_current_user
from app.services.utils import check_owner, db_error_handler

logger = logging.getLogger(__name__)


@db_error_handler
async def create_category(
    category: CategoryBase,
    user: User,
    session: AsyncSession,
) -> Category:
    new_category = Category(
        title=category.title,
        user_id=user.id,
    )
    session.add(new_category)
    await session.commit()
    await session.refresh(new_category)

    logger.info("Category %d from user %d successfully created", new_category.id, user.id)
    return new_category


@db_error_handler
async def update_category(
    category: CategoryBase,
    user: User,
    session: AsyncSession,
    category_id: int = Path(..., ge=1),
) -> Category:
    db_category = await session.get(Category, category_id)
    if not db_category:
        logger.warning("Category with id %d not found", category_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    check_owner(db_category, user.id, "category")

    updated_data = category.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(db_category, key, value)

    session.add(db_category)
    await session.commit()
    await session.refresh(db_category)

    logger.info("Category %d from user %d successfully updated", category_id, user.id)
    return db_category


@db_error_handler
async def delete_category(
    user: User,
    session: AsyncSession,
    category_id: int,
) -> dict:
    db_category = await session.get(Category, category_id)
    if not db_category:
        logger.warning("Category with id %d not found", category_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    check_owner(db_category, user.id, "category")

    await session.delete(db_category)
    await session.commit()

    logger.info("Category %d from user %d successfully deleted", category_id, user.id)
    return {"message": f"Category {category_id} successfully deleted"}


@db_error_handler
async def get_one_category(
    user: User,
    session: AsyncSession,
    category_id: int = Path(..., ge=1),
) -> Category:
    db_category = await session.get(Category, category_id)
    if not db_category:
        logger.warning("Category with id %d not found", category_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    check_owner(db_category, user.id, "category")

    logger.info("Category %d from user %d successfully retrieved", category_id, user.id)
    return db_category


@db_error_handler
async def get_all_category(
    user: User,
    session: AsyncSession,
) -> List[Category]:
    logger.info("Retrieving categories for user %d", user.id)
    result = await session.execute(select(Category).where(Category.user_id == user.id))
    categories = result.scalars().all()
    logger.info("User %d retrieved %d categories", user.id, len(categories))
    return categories
