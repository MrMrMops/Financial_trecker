from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.database import get_async_session
from app.models.auth import User
from app.schemas.auth_schema import UserCreate, UserOut
import bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.db.config import settings
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_password_hash(password: str) -> str:
    """Синхронная функция для хэширования пароля с использованием bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Синхронная функция для проверки пароля."""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def register_user(user: UserCreate, session: AsyncSession):
    try:
        result = await session.execute(select(User).where(User.name == user.name))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Username already registered")

        hashed_password = get_password_hash(user.password)

        new_user = User(
            name=user.name,
            hashed_password=hashed_password,
            email=user.email,
            created_at=datetime.utcnow()
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    except SQLAlchemyError as e:
        logger.error(f"DB error during user registration: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def login_user(user: UserCreate, session: AsyncSession):
    try:
        result = await session.execute(select(User).where(User.name == user.name))
        db_user = result.scalars().first()

        if not db_user or not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid credentials",
                                headers={"WWW-Authenticate": "Bearer"})

        token = create_access_token({"sub": str(db_user.id)})
        return {"access_token": token, "token_type": "bearer"}

    except SQLAlchemyError as e:
        logger.error(f"DB error during user login: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_user(user_id: int, session: AsyncSession):
    try:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except SQLAlchemyError as e:
        logger.error(f"DB error during get_user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )

        result = await session.execute(select(User).where(User.id == int(user_id)))
        user = result.scalars().first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return UserOut(id=user.id, name=user.name, created_at=user.created_at)

    except JWTError as e:
        logger.warning(f"JWT decoding failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except SQLAlchemyError as e:
        logger.error(f"DB error during current user retrieval: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
