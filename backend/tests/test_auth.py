import pytest


@pytest.mark.asyncio
async def test_register_and_login(async_client,authorized_client):
    # Регистрация
    payload = {"name": "newuser", "email": "new@example.com", "password": "secret_password"}
    response = await async_client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"]
    assert data["name"] == payload["name"]

    # Дублирующая регистрация
    dup = await async_client.post("/auth/register", json=payload)
    assert dup.status_code == 400

    # Логин
    login_payload = {"name": payload["name"], "password": payload["password"]}
    response = await async_client.post("/auth/login", json=login_payload)
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token

    # Некорректные креды
    bad = await async_client.post("/auth/login", json={"name": "x", "password": "yyyyyyyyy"})
    assert bad.status_code == 401

    # /me
    headers = {"Authorization": f"Bearer {token}"}
    me = await async_client.get("/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["name"] == payload["name"]