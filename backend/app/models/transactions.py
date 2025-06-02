from typing import List
from unicodedata import category
from unittest.util import _MAX_LENGTH
from sqlalchemy import BigInteger, Float, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.db.config import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    cash: Mapped[float] = mapped_column(Float, nullable=False)

    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("category.id"), nullable=False)
    category = relationship("Category", back_populates="transactions")

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="transactions")



class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    transactions = relationship("Transaction", back_populates="category", cascade="all, delete")