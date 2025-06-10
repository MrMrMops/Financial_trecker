import logging
from fastapi import  Depends, HTTPException, Path, Query, status
from app.models.transactions import Category
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_async_session
from app.services.auth import get_current_user
from app.models.auth import User
from app.schemas.category_schema import CategoryBase
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


async def create_category(
    category: CategoryBase,
    user: User,
    session: AsyncSession,
):
    try:
        new_category = Category(
            title=category.title,
            user_id=user.id
        )

        session.add(new_category)
        await session.commit()
        await session.refresh(new_category)

        logger.info("Category %d from user %d successfully created", new_category.id, user.id)
        return new_category

    except SQLAlchemyError as e:
        logger.error("DB error during category creation: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")


async def update_category(
    category: CategoryBase,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    category_id: int = Path(..., ge=1),
):
    try:
        db_category = await session.get(Category, category_id)

        if not db_category:
            logger.warning("Category with id %d not found", category_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        if db_category.user_id != user.id:
            logger.warning("User %d not authorized to modify category %d", user.id, category_id)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this category")

        updated_data = category.model_dump(exclude_unset=True)
        for key, value in updated_data.items():
            setattr(db_category, key, value)

        session.add(db_category)
        await session.commit()
        await session.refresh(db_category)

        logger.info("Category %d from user %d successfully updated", category_id, user.id)
        return db_category

    except SQLAlchemyError as e:
        logger.error("DB error during category update: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")


async def delete_category(
    user: User,
    session: AsyncSession,
    category_id: int,
):
    try:
        db_category = await session.get(Category, category_id)

        if not db_category:
            logger.warning("Category with id %d not found", category_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        if db_category.user_id != user.id:
            logger.warning("User %d not authorized to delete category %d", user.id, category_id)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this category")

        await session.delete(db_category)
        await session.commit()

        logger.info("Category %d from user %d successfully deleted", category_id, user.id)
        return {"message": f"Category {category_id} successfully deleted"}

    except SQLAlchemyError as e:
        logger.error("DB error during category deletion: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")


async def get_one_category(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    category_id: int = Path(..., ge=1),
):
    try:
        db_category = await session.get(Category, category_id)

        if not db_category:
            logger.warning("Category with id %d not found", category_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

        if db_category.user_id != user.id:
            logger.warning("User %d not authorized to retrieve category %d", user.id, category_id)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to retrieve this category")

        logger.info("Category %d from user %d successfully retrieved", category_id, user.id)
        return db_category

    except SQLAlchemyError as e:
        logger.error("DB error during category retrieval: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")


async def get_all_category(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        logger.info("Retrieving categories for user %d", user.id)
        result = await session.execute(select(Category).where(Category.user_id == user.id))
        categories = result.scalars().all()
        logger.info("User %d retrieved %d categories", user.id, len(categories))
        return categories

    except SQLAlchemyError as e:
        logger.error("DB error during all categories retrieval: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")