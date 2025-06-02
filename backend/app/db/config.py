import os
from pathlib import Path
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
load_dotenv()

class Settings(BaseSettings):
    # DB_HOST: str
    # DB_PORT: str
    # DB_USER: str
    # DB_PASS: str
    # DB_NAME: str
    # JWT_SECRET_KEY: str = 'your_shared_secret'
    # JWT_ALGORITHM: str = "HS256"
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # CACHE_TTL: int = 50000

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://postgres:root@db:5432/financial_trecker_db"

    class Config:
        env_file = 'backend.env'


settings = Settings()
Base = declarative_base()