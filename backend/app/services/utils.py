
from functools import wraps
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from app.exceptions import DatabaseException
import logging

logger = logging.getLogger(__name__)


def check_owner(entity, user_id: int, entity_name: str = "Resource"):
    """
    Проверяет, что объект принадлежит пользователю. Если нет — поднимает HTTPException 403.
    :param entity: ORM объект с атрибутом user_id
    :param user_id: id текущего пользователя
    :param entity_name: имя сущности для сообщения об ошибке
    """
    if getattr(entity, 'user_id', None) != user_id:
        logger.warning("User %d not authorized to access %s %s", user_id, entity_name, getattr(entity, 'id', None))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Not authorized to access this {entity_name}"
        )


def db_error_handler(func):
    """
    Декоратор для обработки SQLAlchemyError: откатит транзакцию и
    перевыбросит в виде DatabaseException.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # session ожидается как именованный параметр session: AsyncSession
        session = kwargs.get('session') or (args[2] if len(args) > 2 else None)
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            logger.error("DB error in %s: %s", func.__name__, str(e))
            if session:
                await session.rollback()
            raise DatabaseException("Internal database error")
    return wrapper
