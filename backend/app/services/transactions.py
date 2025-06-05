from datetime import date
from typing import Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from app.models.transactions import Transaction, Category
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, case, cast, Date
from app.db.database import get_async_session
from app.services.auth import get_current_user
from app.models.auth import User
from app.schemas.transaction_schema import TransactionCreate, TransactionType, TransactionUpdate

# transactions_router = APIRouter(prefix="/transactions", tags=["transactions"])
logger = logging.getLogger(__name__)


async def create_transactions(
        transaction: TransactionCreate,
        user: User,
        session: AsyncSession,
):
    result = await session.execute(select(Category).where(Category.id == transaction.category_id))
    category = result.scalar_one_or_none()

    if category is None:
        logger.warning("Category with id %d not found", transaction.category_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    new_transaction = Transaction(
        title=transaction.title,
        cash=transaction.cash,
        type=transaction.type,
        category_id=transaction.category_id,
        user_id=user.id,
        # created_at=datetime.utcnow(),
    )

    session.add(new_transaction)
    await session.commit()
    await session.refresh(new_transaction)

    logger.info("Transaction %d from user %d successfully created", new_transaction.id, user.id)

    return new_transaction


async def update_transaction(
        transaction: TransactionUpdate,
        user: User,
        session: AsyncSession ,
        transaction_id: int ,
    ):
    
    db_transaction = await session.get(Transaction, transaction_id)

    if not db_transaction:
        logger.warning("Transaction with id %d not found", transaction_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    if db_transaction.user_id != user.id:
        logger.warning("User %d not authorized to modify transaction %d", user.id, transaction_id)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this transaction")

    updated_data = transaction.model_dump(exclude_unset=True)

    category_id = updated_data.get("category_id")
    if category_id is not None:
        result = await session.execute(select(Category).where(Category.id == category_id))
        category = result.scalar_one_or_none()
        if category is None:
            logger.warning("Category with id %d not found", category_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    for key, value in updated_data.items():
        setattr(db_transaction, key, value)

    session.add(db_transaction)
    await session.commit()
    await session.refresh(db_transaction)

    logger.info("Transaction %d from user %d successfully updated", transaction_id, user.id)
    return db_transaction


async def delete_transaction(
        user: User,
        session: AsyncSession,
        transaction_id: int ,
):
    db_transaction = await session.get(Transaction, transaction_id)

    if not db_transaction:
        logger.warning("Transaction with id %d not found", transaction_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    
    if db_transaction.user_id != user.id:
        logger.warning("User %d not authorized to delete transaction %d", user.id, transaction_id)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this transaction")
    
    await session.delete(db_transaction)
    await session.commit()
    logger.info("Transaction %d from user %d successfully deleted", transaction_id, user.id)
    return {'message': f'Transaction {transaction_id} successfully deleted'}


async def get_one_transaction(
        user: User ,
        session: AsyncSession ,
        transaction_id: int,
):
    db_transaction = await session.get(Transaction, transaction_id)

    if not db_transaction:
        logger.warning("Transaction with id %d not found", transaction_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    
    if db_transaction.user_id != user.id:
        logger.warning("User %d not authorized to retrieve transaction %d", user.id, transaction_id)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to retrieve this transaction")
    
    logger.info("Transaction %d from user %d successfully retrieved", transaction_id, user.id)
    return db_transaction

async def get_transactions(
    user: User,
    session: AsyncSession,
    type: Optional[TransactionType],
    start_date: Optional[date],
    end_date: Optional[date],
    category_id: Optional[int],
):
    query = select(Transaction).where(Transaction.user_id == user.id)

    if type is not None:
        query = query.where(Transaction.type == type)
    if start_date is not None:
        query = query.where(Transaction.created_at >= start_date)
    if end_date is not None:
        query = query.where(Transaction.created_at <= end_date)
    if category_id is not None:
        query = query.where(Transaction.category_id == category_id)


    result = await session.execute(query)
    transactions = result.scalars().all()
    logger.info("User %d retrieved %d transactions", user.id, len(transactions))

    return transactions
    

async def get_balance(user: User, session: AsyncSession, current_date: Optional[date]):
    if current_date is None:
        current_date = date.today()
        
    income_sum = await session.scalar(
        select(func.sum(Transaction.cash))
        .where(Transaction.user_id == user.id, Transaction.type == TransactionType.income, cast(Transaction.created_at, Date) <= current_date)
    )

    expense_sum = await session.scalar(
        select(func.sum(Transaction.cash))
        .where(Transaction.user_id == user.id, Transaction.type == TransactionType.expense, cast(Transaction.created_at, Date) <= current_date)
    )

    income_sum = income_sum or 0
    expense_sum = expense_sum or 0

    balance = income_sum - expense_sum

    logger.info(f"Balance %d on date {current_date} from user %d successfully retrieved", balance, user.id)
    return balance
