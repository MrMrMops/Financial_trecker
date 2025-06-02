import logging
import os
from pathlib import Path
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


env_path = Path(__file__).resolve().parents[3] / '.env'
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):

    JWT_SECRET_KEY: str 
    JWT_ALGORITHM: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CACHE_TTL: int = 50000

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://postgres:root@db:5432/financial_trecker_db"

    class Config:
        env_file = str(env_path)


settings = Settings()
class Base(DeclarativeBase):
    pass


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)