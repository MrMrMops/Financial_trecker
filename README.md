# Financial_trecker
Вот профессиональное руководство для `README.md`, описывающее **запуск проекта с помощью Docker и Docker Compose**. Подходит для вашего проекта финансового трекера.

---

## 🚀 Запуск проекта с Docker

### 📋 Предварительные требования

Перед запуском убедитесь, что у вас установлены:

* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/) (если используете Docker < v2)

---

### 🧾 1. Клонируйте репозиторий

```bash
git clone https://github.com/ВАШ_ПОЛЬЗОВАТЕЛЬ/ВАШ_ПРОЕКТ.git
cd ВАШ_ПРОЕКТ
```

---

### ⚙️ 2. Создайте `.env` файл

Создайте файл `.env` в корне проекта и укажите переменные окружения. Пример:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=root
POSTGRES_DB=financial_trecker_db

DATABASE_URL=postgresql+asyncpg://postgres:root@db:5432/financial_trecker_db

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
```

---

### 🛠 3. Соберите и запустите контейнеры

```bash
docker-compose up --build
```

Это выполнит:

* сборку образов приложения и воркера Celery
* запуск контейнеров PostgreSQL, Redis, FastAPI и Celery
* проброс портов:

  * `localhost:8000` — веб-сервис (FastAPI)
  * `localhost:5432` — PostgreSQL
  * `localhost:6379` — Redis

---

### 📦 4. Примените миграции (если необходимо)

Если миграции не запускаются автоматически, выполните вручную:

```bash
docker exec -it financialTrecker alembic upgrade head
```

---

### ✅ 5. Проверьте запуск

* Перейдите в браузере по адресу: [http://localhost:8000/docs](http://localhost:8000/docs)
* Вы должны увидеть автоматически сгенерированную Swagger-документацию от FastAPI.

---

### 🧪 6. (опционально) Запуск тестов

```bash
docker exec -it financialTrecker pytest
```

---

### 🧹 Остановка и удаление контейнеров

```bash
docker-compose down
```

Если хотите удалить тома (например, базу данных):

```bash
docker-compose down -v
```


