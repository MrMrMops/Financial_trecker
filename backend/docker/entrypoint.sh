#!/bin/sh

# Применить все миграции к БД
alembic upgrade head

# Запустить FastAPI-сервер
exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000