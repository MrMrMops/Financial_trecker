from datetime import date, datetime
from io import StringIO
from typing import Optional
import logging
from fastapi import Depends, HTTPException, Query, status
from app.models.transactions import Transaction, Category
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import asc, desc, extract, func, cast, Date
from app.db.database import get_async_session
from app.services.auth import get_current_user
from app.models.auth import User
from app.schemas.transaction_schema import SortableTransactionFields, TransactionCreate, TransactionType, TransactionUpdate
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import StreamingResponse
import pandas as pd

logger = logging.getLogger(__name__)


async def create_transactions(transaction: TransactionCreate, user: User, session: AsyncSession):
    try:
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
        )

        session.add(new_transaction)
        await session.commit()
        await session.refresh(new_transaction)

        logger.info("Transaction %d from user %d successfully created", new_transaction.id, user.id)
        return new_transaction

    except SQLAlchemyError as e:
        logger.error("DB error during transaction creation: %s", str(e))
        await session.rollback()
        raise HTTPException(status_code=500, detail="Database error")


async def update_transaction(transaction: TransactionUpdate, user: User, session: AsyncSession, transaction_id: int):
    try:
        db_transaction = await session.get(Transaction, transaction_id)

        if not db_transaction:
            logger.warning("Transaction with id %d not found", transaction_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

        if db_transaction.user_id != user.id:
            logger.warning("User %d not authorized to modify transaction %d", user.id, transaction_id)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

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

    except SQLAlchemyError as e:
        logger.error("DB error during transaction update: %s", str(e))
        await session.rollback()
        raise HTTPException(status_code=500, detail="Database error")


async def delete_transaction(user: User, session: AsyncSession, transaction_id: int):
    try:
        db_transaction = await session.get(Transaction, transaction_id)

        if not db_transaction:
            logger.warning("Transaction with id %d not found", transaction_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

        if db_transaction.user_id != user.id:
            logger.warning("User %d not authorized to delete transaction %d", user.id, transaction_id)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        await session.delete(db_transaction)
        await session.commit()

        logger.info("Transaction %d from user %d successfully deleted", transaction_id, user.id)
        return {'message': f'Transaction {transaction_id} successfully deleted'}

    except SQLAlchemyError as e:
        logger.error("DB error during transaction deletion: %s", str(e))
        await session.rollback()
        raise HTTPException(status_code=500, detail="Database error")


async def get_one_transaction(user: User, session: AsyncSession, transaction_id: int):
    try:
        db_transaction = await session.get(Transaction, transaction_id)

        if not db_transaction:
            logger.warning("Transaction with id %d not found", transaction_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

        if db_transaction.user_id != user.id:
            logger.warning("User %d not authorized to retrieve transaction %d", user.id, transaction_id)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

        logger.info("Transaction %d from user %d successfully retrieved", transaction_id, user.id)
        return db_transaction

    except SQLAlchemyError as e:
        logger.error("DB error during transaction retrieval: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")


async def get_transactions(user: User, session: AsyncSession,
    type: Optional[TransactionType],
    start_date: Optional[date],
    end_date: Optional[date],
    category_id: Optional[int],
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: SortableTransactionFields = Query("created_at"),
    order: str = Query("desc")):

    try:
        query = select(Transaction).where(Transaction.user_id == user.id)

        if type is not None:
            query = query.where(Transaction.type == type)
        if start_date is not None:
            query = query.where(Transaction.created_at >= start_date)
        if end_date is not None:
            query = query.where(Transaction.created_at <= end_date)
        if category_id is not None:
            query = query.where(Transaction.category_id == category_id)

        order_func = desc if order.lower() == "desc" else asc
        query = query.order_by(order_func(getattr(Transaction, sort_by)))
        query = query.limit(limit).offset(offset)

        result = await session.execute(query)
        transactions = result.scalars().all()

        logger.info("User %d retrieved %d transactions", user.id, len(transactions))
        return transactions

    except SQLAlchemyError as e:
        logger.error("DB error during transaction list retrieval: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")
    

async def get_balance(user: User, session: AsyncSession, current_date: Optional[date]) -> int:
    try:
        if current_date is None:
            current_date = date.today()

        stmt = (
            select(
                Transaction.type,
                func.coalesce(func.sum(Transaction.cash), 0)
            )
            .where(
                Transaction.user_id == user.id,
                cast(Transaction.created_at, Date) <= current_date
            )
            .group_by(Transaction.type)
        )

        result = await session.execute(stmt)
        rows = result.fetchall()

        income_sum = 0
        expense_sum = 0

        for tx_type, total in rows:
            if tx_type == TransactionType.income:
                income_sum = total
            elif tx_type == TransactionType.expense:
                expense_sum = total

        balance = income_sum - expense_sum
        logger.info(f"Balance {balance} on date {current_date} from user {user.id} successfully retrieved")
        return balance

    except SQLAlchemyError as e:
        logger.error("DB error during balance calculation: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")


async def get_analitics_on_month(user: User, session: AsyncSession, year: int, month: int):
    try:
        stmt = (
            select(
                Transaction.type,
                func.sum(Transaction.cash).label("total")
            )
            .where(
                Transaction.user_id == user.id,
                extract("month", Transaction.created_at) == month,
                extract("year", Transaction.created_at) == year
            )
            .group_by(Transaction.type)
        )

        result = await session.execute(stmt)
        rows = result.fetchall()

        income_sum = 0
        expense_sum = 0

        for type_, total in rows:
            if type_ == TransactionType.income:
                income_sum = total
            elif type_ == TransactionType.expense:
                expense_sum = total

        logger.info("Income %d and Expense %d for %d-%02d retrieved", income_sum, expense_sum, year, month)

        return {
            "month": f"{year}-{month:02d}",
            "income": income_sum,
            "expense": expense_sum
        }

    except SQLAlchemyError as e:
        logger.error("DB error during monthly analytics retrieval: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")


async def get_analitics_on_category(
    user: User,
    session: AsyncSession,
    start_date: Optional[date],
    end_date: Optional[date],
    category_id: Optional[int],
):
    try:
        query = (
            select(
                Transaction.type,
                func.sum(Transaction.cash).label("total")
            )
            .where(Transaction.user_id == user.id)
            .group_by(Transaction.type)
        )

        if start_date is not None:
            query = query.where(Transaction.created_at >= start_date)
        if end_date is not None:
            query = query.where(Transaction.created_at <= end_date)
        if category_id is not None:
            query = query.where(Transaction.category_id == category_id)

        result = await session.execute(query)
        rows = result.fetchall()

        income_sum = 0
        expense_sum = 0

        for type_, total in rows:
            if type_ == TransactionType.income:
                income_sum = total
            elif type_ == TransactionType.expense:
                expense_sum = total

        logger.info("Analytics by category_id=%s retrieved for user %d", category_id, user.id)
        return {
            "income": income_sum,
            "expense": expense_sum,
            "category_id": category_id
        }

    except SQLAlchemyError as e:
        logger.error("DB error during category analytics retrieval: %s", str(e))
        raise HTTPException(status_code=500, detail="Database error")


async def export_transactions_csv(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    try:
        # Получаем транзакции пользователя
        result = await session.execute(
            select(Transaction).where(Transaction.user_id == user.id)
        )
        transactions = result.scalars().all()

        if not transactions:
            return StreamingResponse(
                iter(["id,title,cash,type,category_id,created_at\n"]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=empty.csv"}
            )

        # Преобразуем в pandas DataFrame
        data = [
            {
                "id": t.id,
                "title": t.title,
                "cash": t.cash,
                "type": t.type,
                "category_id": t.category_id,
                "created_at": t.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for t in transactions
        ]
        df = pd.DataFrame(data)

        # Сохраняем в память (буфер)
        buffer = StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)

        filename = f"transactions_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

        return StreamingResponse(
            iter([buffer.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        logger.exception("Ошибка при экспорте транзакций")
        raise HTTPException(status_code=500, detail="Ошибка при экспорте данных")