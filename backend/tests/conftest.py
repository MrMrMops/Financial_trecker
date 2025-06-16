import logging
import uuid
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import  create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.db.database import get_async_session,async_session
from app.db.base import Base
from app.models.auth import User
from app.models.transactions import Category, Transaction
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from app.services.auth import create_access_token, get_password_hash
from app.schemas.transaction_schema import TransactionType
from httpx import AsyncClient
from app.main import app

# ⚠ Убедитесь, что у вас есть test-база
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@financial_test_db:5432/test_financial_db"
logger = logging.getLogger(__name__)

engine_test = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool, echo=True)

# 2. Создаем асинхронную сессию
AsyncTestingSession = async_sessionmaker(engine_test, expire_on_commit=False)


@pytest.fixture
def sync_session():
    sync_engine_test = create_engine(
        "postgresql+psycopg2://postgres:postgres@financial_test_db:5432/test_financial_db"
    )
    TestingSyncSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=sync_engine_test
)
    with TestingSyncSessionLocal() as session:
        yield session


# 3. Фикстура для инициализации БД - УБИРАЕМ autouse!
@pytest.fixture(scope="session", autouse=True)
def init_models():
    sync_engine = create_engine('postgresql+psycopg2://postgres:postgres@financial_test_db:5432/test_financial_db')

    # Синхронное создание/удаление таблиц
    Base.metadata.drop_all(sync_engine)
    Base.metadata.create_all(sync_engine)
    yield
    Base.metadata.drop_all(sync_engine)
    # Очистка после тестов

@pytest_asyncio.fixture
async def db_session():
    async with AsyncTestingSession() as session:
        yield session



@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
        
@pytest_asyncio.fixture
async def authorized_client():
    # Переопределяем зависимость
    async def override_get_session():
        async with AsyncTestingSession() as session:
            yield session

    app.dependency_overrides[get_async_session] = override_get_session

    # Создаём пользователя и токен в одной сессии
    async with AsyncTestingSession() as session:
        unique_email = f"test_{uuid.uuid4().hex}@example.com"
        user = User(name = f"user_{uuid.uuid4().hex[:6]}", email = unique_email, hashed_password = get_password_hash("secret") )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token({"sub": str(user.id)})

    # Клиент с токеном
    headers = {"Authorization": f"Bearer {token}"}
    async with AsyncClient(app=app, base_url="http://test", headers=headers) as client:
        yield client

    app.dependency_overrides.clear()

@pytest_asyncio.fixture()
async def category_id(db_session):
    category = Category(
        title="Groceries",
        user_id=1
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)   

    return category.id
