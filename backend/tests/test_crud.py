import pytest
from httpx import AsyncClient
from app.main import app
from app.schemas.transaction_schema import TransactionType

# CRUD CATEGORY

@pytest.mark.asyncio
async def test_create_category(authorized_client):
    payload = {"title": "New category"}
    response = await authorized_client.post("/categories/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]

@pytest.mark.asyncio
async def test_get_all_categories(authorized_client):
    response = await authorized_client.get("/categories/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_update_category(authorized_client):
    create_resp = await authorized_client.post("/categories/", json={"title": "Old title"})
    category_id = create_resp.json()["id"]

    update_payload = {"title": "Updated title"}
    update_resp = await authorized_client.patch(f"/categories/{category_id}", json=update_payload)
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["title"] == update_payload["title"]

@pytest.mark.asyncio
async def test_delete_category(authorized_client):
    create_resp = await authorized_client.post("/categories/", json={"title": "Delete me"})
    category_id = create_resp.json()["id"]

    delete_resp = await authorized_client.delete(f"/categories/{category_id}")
    assert delete_resp.status_code == 200

@pytest.mark.asyncio
async def test_get_category_success(authorized_client):
    # Создаем категорию для текущего пользователя
    create_resp = await authorized_client.post("/categories/", json={"title": "Test Category"})
    assert create_resp.status_code == 201
    category_id = create_resp.json()["id"]

    # Запрашиваем созданную категорию
    get_resp = await authorized_client.get(f"/categories/{category_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == category_id
    assert data["title"] == "Test Category"


# CRUD TRANSACTION

@pytest.mark.asyncio
async def test_create_transaction(authorized_client):
    payload = {
        "title": "Test transaction",
        "cash": 150.0,
        "type": "income",  # enum TransactionType as string
        "category_id": 1
    }
    response = await authorized_client.post("/transactions/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["cash"] == payload["cash"]
    assert data["type"] == payload["type"]
    assert data["category_id"] == payload["category_id"]

@pytest.mark.asyncio
async def test_get_all_transactions(authorized_client):
    response = await authorized_client.get("/transactions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    

@pytest.mark.asyncio
async def test_get_transaction_by_id(authorized_client):
    # Сначала создаём категорию и транзакцию
    category_resp = await authorized_client.post("/categories/", json={"title": "Temporary"})
    category_id = category_resp.json()["id"]

    transaction_payload = {
        "title": "One transaction",
        "cash": 200.0,
        "type": "expense",
        "category_id": category_id
    }
    create_resp = await authorized_client.post("/transactions/", json=transaction_payload)
    transaction_id = create_resp.json()["id"]

    # Теперь получаем транзакцию по id
    response = await authorized_client.get(f"/transactions/{transaction_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == transaction_id

@pytest.mark.asyncio
async def test_update_transaction(authorized_client):
    category_resp = await authorized_client.post("/categories/", json={"title": "UpdateCat"})
    category_id = category_resp.json()["id"]

    create_resp = await authorized_client.post("/transactions/", json={
        "title": "To update",
        "cash": 300.0,
        "type": "income",
        "category_id": category_id
    })
    transaction_id = create_resp.json()["id"]

    update_payload = {
        "title": "Updated title",
        "cash": 400.0,
        "type": "expense",
        "category_id": category_id
    }
    update_resp = await authorized_client.patch(f"/transactions/{transaction_id}", json=update_payload)
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["title"] == update_payload["title"]
    assert data["cash"] == update_payload["cash"]
    assert data["type"] == update_payload["type"]

@pytest.mark.asyncio
async def test_delete_transaction(authorized_client):
    category_resp = await authorized_client.post("/categories/", json={"title": "DeleteCat"})
    category_id = category_resp.json()["id"]

    create_resp = await authorized_client.post("/transactions/", json={
        "title": "To delete",
        "cash": 100.0,
        "type": "income",
        "category_id": category_id
    })
    transaction_id = create_resp.json()["id"]

    delete_resp = await authorized_client.delete(f"/transactions/{transaction_id}")
    assert delete_resp.status_code == 200


# OTHER TRANSACTION ROUTES 

@pytest.mark.asyncio
async def test_get_balance_route_authorized(authorized_client):
    response = await authorized_client.get("/transactions/balance")
    assert response.status_code == 200
    assert isinstance(response.json(), int)


@pytest.mark.asyncio
async def test_get_analitics_on_month_route(authorized_client):
    year = 2025
    month = 6
    response = await authorized_client.get(f"/transactions/analytics?year={year}&month={month}")

    assert response.status_code == 200
    data = response.json()
    assert "month" in data
    assert "income" in data
    assert "expense" in data

@pytest.mark.asyncio
async def test_get_analitics_on_category_route(authorized_client):
    category_resp = await authorized_client.post("/categories/", json={"title": "CategoryTest"})
    category_id = category_resp.json()["id"]

    # Запрашиваем аналитику по категории без дат — за весь период
    response = await authorized_client.get(
        "/transactions/category_analytics",
        params={"category_id": category_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert "income" in data
    assert "expense" in data
    assert data["category_id"] == category_id

@pytest.mark.asyncio
async def test_get_all_transactions_route_with_filters(authorized_client):
    category_resp = await authorized_client.post("/categories/", json={"title": "FilterCat"})
    category_id = category_resp.json()["id"]

    # Создаем несколько транзакций
    await authorized_client.post("/transactions/", json={
        "title": "Income TX",
        "cash": 100,
        "type": "income",
        "category_id": category_id
    })
    await authorized_client.post("/transactions/", json={
        "title": "Expense TX",
        "cash": 50,
        "type": "expense",
        "category_id": category_id
    })

    params = {
        "type": "income",
        "category_id": category_id,
        "limit": 10,
        "offset": 0,
        "sort_by": "created_at",
        "order": "desc"
    }

    response = await authorized_client.get("/transactions/", params=params)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for tx in data:
        assert tx["type"] == "income"

@pytest.mark.asyncio
async def test_export_transactions_csv_route(authorized_client):
    response = await authorized_client.get("/transactions/export")
    assert response.status_code == 200
    # Проверим заголовки, что это csv-файл вложением
    content_disposition = response.headers.get("content-disposition")
    assert content_disposition is not None
    assert "attachment" in content_disposition
    assert response.headers.get("content-type") == "text/csv; charset=utf-8"
    content = await response.aread()
    # Контент CSV должен содержать заголовки
    assert b"id,title,cash,type,category_id,created_at" in content