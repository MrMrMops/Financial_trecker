import asyncio
from unittest.mock import patch, AsyncMock
import pytest
from sqlalchemy import create_engine
from app.tasks.export import export_transactions_to_csv
from app.models.transactions import Transaction
from app.models.auth import User
import pytest
from sqlalchemy.orm import sessionmaker

from app.schemas.transaction_schema import TransactionType



@pytest.mark.asyncio
async def test_export_csv_start(authorized_client):
    response = await authorized_client.post("/api/export/")
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["detail"] == "Экспорт запущен"


@pytest.mark.asyncio
async def test_get_export_status_completed(authorized_client):
    response = await authorized_client.post("/api/export/")
    assert response.status_code == 200
    task_id = response.json()["task_id"]

    # Пробуем опрашивать статус с интервалом
    for _ in range(10):  # до 10 попыток
        await asyncio.sleep(1)
        status_resp = await authorized_client.get(f"/api/export/status/{task_id}")
        status_data = status_resp.json()

        if status_data["status"] == "completed":
            assert "file_url" in status_data
            break
        elif status_data["status"] == "failed":
            pytest.fail("Celery task failed")
    else:
        pytest.fail(f"Celery task did not complete in time {response.json()}, {status_resp.json()}")


@pytest.mark.asyncio
async def test_export_flow(authorized_client):
    resp = await authorized_client.post("/api/export/")
    assert resp.status_code == 200
    task_id = resp.json()["task_id"]
    # подождать выполнения
    for _ in range(5):
        await asyncio.sleep(1)
        status = await authorized_client.get(f"/api/export/status/{task_id}")
        if status.json().get("status") == "completed":
            assert status.json().get("file_url")
            break
    else:
        pytest.fail("Export task did not complete")