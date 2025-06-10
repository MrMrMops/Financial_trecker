from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.models.auth import User
from app.services.auth import get_current_user
from app.tasks.export import export_transactions_to_csv
from app.db.config import celery_app
from celery.result import AsyncResult

export_router = APIRouter(prefix="/api/export", tags=["Export"])


@export_router.post(
    "/",
    response_class=JSONResponse,
    summary="Запуск задачи экспорта транзакций",
    description=(
        "Запускает фоновую задачу экспорта всех транзакций пользователя в CSV-файл. "
        "После завершения задачи можно получить ссылку на файл через эндпоинт `/export/status/{task_id}`."
    ),
)
async def export_csv(current_user: User = Depends(get_current_user)):
    task = export_transactions_to_csv.delay(current_user.id)
    return {"task_id": task.id, "detail": "Экспорт запущен"}


@export_router.get(
    "/status/{task_id}",
    response_class=JSONResponse,
    summary="Проверка статуса задачи экспорта",
    description=(
        "Позволяет узнать статус фоново выполняемой задачи экспорта транзакций в CSV. "
        "Если задача завершена успешно, возвращается ссылка на файл. "
        "Иначе — текущий статус: PENDING, STARTED, FAILURE и др."
    ),)
async def get_export_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    
    if result.state == "PENDING":
        return {"status": "pending"}
    elif result.state == "SUCCESS":
        return {"status": "completed", "file_url": result.result}
    elif result.state == "FAILURE":
        return {"status": "failed", "error": str(result.result)}
    else:
        return {"status": result.state}

