from celery import Celery
from dotenv import load_dotenv
from pydantic import SecretStr, EmailStr
from pydantic_settings import BaseSettings
import logging

env_path ='.env' 
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):

    CELERY_RESULT_BACKEND : str
    CELERY_BROKER_URL : str
    JWT_SECRET_KEY: str 
    JWT_ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CACHE_TTL: int = 50000

    ASYNC_DATABASE_URL: str = "postgresql+asyncpg://postgres:root@db:5432/financial_trecker_db"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://postgres:root@db:5432/financial_trecker_db"
    
    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD : str
    MAIL_FROM : str
    MAIL_SERVER : str
    MAIL_PORT : int

    class Config:
        env_file = str(env_path)


settings = Settings()



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

celery_app = Celery(
    "financial_tracker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.export"] ,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    
)


