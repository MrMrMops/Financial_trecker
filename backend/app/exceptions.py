from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class DatabaseException(Exception):
    """Кастомное исключение для ошибок базы данных"""
    def __init__(self, detail: str = "Database error"):
        self.detail = detail


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"DB error: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal database error"})

async def database_exception_handler(request: Request, exc: DatabaseException):
    logger.error(f"Custom DB exception: {exc.detail}")
    return JSONResponse(status_code=500, content={"detail": exc.detail})

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})