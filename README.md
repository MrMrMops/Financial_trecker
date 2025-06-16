# Financial Trecker

**Financial Trecker** — это асинхронное веб-приложение для учёта личных финансов. Проект позволяет пользователям создавать категории, добавлять транзакции (доходы и расходы), получать аналитику, экспортировать отчёты в CSV и отправлять их по электронной почте.

---

## 🚀 Особенности

* **Регистрация и аутентификация** с JWT (FastAPI + OAuth2).
* **CRUD для категорий** и **транзакций** с передачей прав пользователя.
* **Отчёты & аналитика**:

  * Баланс на любую дату.
  * Месячная аналитика (доход/расход).
  * Аналитика по категориям.
* **Экспорт в формате CSV**:

  * Синхронный экспорт через HTTP.
  * Фоновый экспорт с Celery, Redis и отправкой письма пользователю.
* **Документация Swagger** (FastAPI автоматически генерирует `/docs`).
* **Асинхронная архитектура** (FastAPI + Async SQLAlchemy).
* **Контейнеризация**: Docker Compose для продакшена и тестов.
* **Полное покрытие тестами** (pytest, pytest-asyncio, httpx).
* **CI/CD**: GitHub Actions запускает тесты и деплой.

---

## 🏗 Технологический стек

* **Python 3.11**
* **FastAPI** — веб-фреймворк
* **SQLAlchemy 2.0 (async)** для работы с PostgreSQL
* **Alembic** — управление миграциями БД
* **Pydantic** — валидация данных
* **Celery + Redis** — фоновые задачи
* **Docker & Docker Compose** — контейнеризация
* **pytest, pytest-asyncio, httpx** — тестирование
* **GitHub Actions** — CI/CD

---

## 📥 Установка

1. **Клонируйте репозиторий**

   ```bash
   git clone https://github.com/MrMrMops/Financial_trecker.git
   cd Financial_trecker
   ```

2. **Создайте `.env`** в корне проекта, заполните переменные (пример `.env.example`):

   ```properties
   DATABASE_URL=postgresql+asyncpg://user:password@db:5432/financial_trecker_db
   SYNC_DATABASE_URL=postgresql+psycopg2://user:password@db:5432/financial_trecker_db
   JWT_SECRET_KEY=your_secret_key
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   MAIL_USERNAME=...
   MAIL_PASSWORD=...
   MAIL_FROM=...
   MAIL_SERVER=...
   MAIL_PORT=587
   CELERY_BROKER_URL=redis://redis:6379/0
   CELERY_RESULT_BACKEND=redis://redis:6379/1
   ```

3. **Запустите Docker Compose**

   ```bash
   docker-compose -f docker/docker-compose.yml up --build -d
   ```

4. **Примените миграции** (если не настроено в `entrypoint.sh`):

   ```bash
   docker-compose exec web alembic upgrade head
   ```

5. **Откройте документацию**

   * Swagger UI: `http://localhost:8000/docs`
   * Redoc: `http://localhost:8000/redoc`

---

## ⚙️ Структура проекта

```
├── app
│   ├── main.py            # создание FastAPI-приложения
│   ├── db
│   │   ├── base.py        # Declarative Base
│   │   ├── database.py    # AsyncSession, SyncSessionLocal
│   │   ├── config.py      # настройки Celery и Redis
│   ├── models             # ORM-модели (User, Category, Transaction)
│   ├── schemas            # Pydantic-схемы
│   ├── services           # бизнес-логика
│   ├── routers            # HTTP-маршруты
│   ├── tasks              # Celery-задачи
│   └── utils              # вспомогательные модули (логика проверки, декораторы)
├── tests
│   ├── conftest.py        # фикстуры pytest
│   ├── test_auth.py       # тесты аутентификации
│   ├── test_categories_*.py  # тесты категорий
│   ├── test_transactions_*.py # тесты транзакций
│   ├── test_export_*.py   # тесты экспорта
│   └── docker-compose.test.yml # окружение для тестов
├── docker
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── docker-compose.yml # для продакшена
├── alembic               # миграции Alembic
├── .github
│   └── workflows
│       └── ci.yml         # GitHub Actions CI/CD
├── README.md
└── .env.example
```

---

## 🔬 Тестирование

1. **Запуск тестов** (локально без Docker):

   ```bash
   pytest -v
   ```

2. **Через Docker Compose**:

   ```bash
   docker-compose -f tests/docker-compose.test.yml up --build --abort-on-container-exit
   docker-compose -f tests/docker-compose.test.yml down
   ```

---

## 📦 CI/CD

* **GitHub Actions**: при пуше в `main` или PR выполняются тесты, после тестов — деплой образов.
* **Кэширование Docker layers** ускоряет сборку.
* **Миграции** Alembic автоматически применяются при старте контейнеров.

---

## ❓ Как внести изменения

1. Создайте ветку от `main`: `git checkout -b feature/your-feature`
2. Сделайте изменения, добавьте тесты.
3. Откройте PR, дождитесь прохождения CI и ревью.

---

## 📄 Лицензия

MIT © MrMrMops
