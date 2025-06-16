from datetime import date

from typing import List, Optional
from fastapi import APIRouter, Path, Query, status, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import User
from app.schemas.transaction_schema import SortableTransactionFields, TransactionCreate, TransactionOut, TransactionType, TransactionUpdate
from app.services.auth import get_current_user
from app.db.database import get_async_session
from app.services.transactions import (
    create_transactions,
    delete_transaction,
    export_transactions_csv,
    get_analitics_on_category,
    get_analitics_on_month,
    get_balance,
    get_transactions,
    get_one_transaction,
    update_transaction,
)

transactions_router = APIRouter(prefix="/transactions", tags=["transactions"])


@transactions_router.post(
    '/',
    response_model=TransactionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создание транзакции",
    description="Создает новую транзакцию для текущего пользователя. Требуются данные: название, сумма и категория."
)
async def create_transaction(
        transaction: TransactionCreate,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)):
    return await create_transactions(transaction=transaction, user=user, session=session)


@transactions_router.patch(
    '/{transaction_id}',
    response_model=TransactionOut,
    summary="Обновление транзакции",
    description="Обновляет существующую транзакцию по ID. Разрешено частичное обновление. "
                "Только владелец транзакции может её изменить."
)
async def update_transaction_route(
        transaction: TransactionUpdate,
        transaction_id: int = Path(..., ge=1),
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)):
    return await update_transaction(transaction, user, session, transaction_id)


@transactions_router.delete(
    '/{transaction_id}',
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Удаление транзакции",
    description="Удаляет транзакцию по ID. Доступно только владельцу."
)
async def delete_transaction_route(
        transaction_id: int = Path(..., ge=1),
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)):
    return await delete_transaction(user, session, transaction_id)

@transactions_router.get(
    '/analytics',
    response_model=dict,
    summary="Получить Доходы и расходы на месяц",
    description=(
        "Возвращает месяц, доходы и расходы за месяц ")
)
async def get_analitics_on_month_route(
    year: int, 
    month: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),

    ):
    return await get_analitics_on_month(user,session,year,month)

@transactions_router.get(
    '/category_analytics',
    response_model=dict,
    summary="Получить Доходы и расходы по категории",
    description=(
        "Возвращает доходы и расходы по категории, если сроки не указаны, считает за весь период")
)
async def get_analitics_on_category_route(
    category_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    user: User= Depends(get_current_user), 
    session: AsyncSession = Depends(get_async_session),
    ):

    return await get_analitics_on_category(user,session,start_date,end_date,category_id)

@transactions_router.get(
    '/balance',
    response_model=int,
    summary="Получить баланс",
    description=(
        "Возвращает число - баланс на указанную дату, если дата не указана то считается на текущий день")
)
async def get_balance_route(
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
        current_date: Optional[date] = None,    
        ):
    
    return await get_balance(user,session,current_date)
    

@transactions_router.get(
    '/',
    response_model=List[TransactionOut],
    summary="Получить список транзакций",
    description=(
        "Возвращает список транзакций пользователя с возможностью фильтрации по:\n"
        "- типу транзакции (`income` или `expense`)\n"
        "- диапазону дат (`start_date`, `end_date`)\n\n"
        "Если фильтры не указаны, возвращаются все транзакции пользователя.")
)
async def get_all_transactions_route(
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session),
        type: Optional[TransactionType] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None,
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0),
        sort_by: SortableTransactionFields = Query("created_at"),
        order: str = Query("desc")
        ):
    return await get_transactions(user, session,type,start_date,end_date, category_id,limit,offset,sort_by,order)


@transactions_router.get(
    "/export",
    response_class=StreamingResponse,
    summary="Экспорт транзакций в формате CSV",
    description=(
        "Экспортирует все транзакции текущего авторизованного пользователя в CSV-файл. "
        "Файл формируется в памяти и возвращается как вложение без сохранения на диск. "
        "Поддерживает экспорт полей: id, title, cash, type, category_id, created_at."
    )
)
async def export_transactions_csv_route(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    return await export_transactions_csv(user,session)


@transactions_router.get(
    '/{transaction_id}',
    response_model=TransactionOut,
    summary="Получить одну транзакцию",
    description="Возвращает данные конкретной транзакции по её ID. Доступно только владельцу."
)
async def get_transaction_route(
        transaction_id: int = Path(..., ge=1),
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)):
    return await get_one_transaction(user, session, transaction_id)