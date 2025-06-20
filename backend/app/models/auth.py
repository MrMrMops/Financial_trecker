from typing import List
from unittest.util import _MAX_LENGTH
from sqlalchemy import BigInteger, String, DateTime
from sqlalchemy.orm import relationship
from app.models.transactions import Transaction
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name : Mapped[str] = mapped_column(String(50), nullable=False)
    email : Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    transactions : Mapped[List[Transaction]] = relationship('Transaction', back_populates='user',cascade='all, delete-orphan')
    categories = relationship("Category", back_populates="user")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())