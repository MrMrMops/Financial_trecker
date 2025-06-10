import pytest
from datetime import datetime

from app.models.auth import User
from app.models.transactions import Category, Transaction
from app.schemas.transaction_schema import TransactionType  # Или используйте ваш enum напрямую
from sqlalchemy import inspect, text

from app.db.base import Base


@pytest.mark.asyncio
async def test_create_user(db_session):
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    await db_session.commit()

@pytest.mark.asyncio
async def test_create_category(db_session):
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    await db_session.flush()  # Без коммита, чтобы не терять контроль

    category = Category(
        title="Groceries",
        user_id=user.id
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    assert category.id is not None
    assert category.title == "Groceries"
    assert category.user_id == user.id


@pytest.mark.asyncio
async def test_create_transaction(db_session):
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    await db_session.flush()

    category = Category(
        title="Food",
        user_id=user.id
    )
    db_session.add(category)
    await db_session.flush()

    transaction = Transaction(
        title="Dinner",
        cash=25.0,
        type=TransactionType.expense,
        user_id=user.id,
        category_id=category.id
    )
    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(transaction)

    assert transaction.id is not None
    assert transaction.cash == 25.0
    assert transaction.type == TransactionType.expense
