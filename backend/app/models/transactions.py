from sqlalchemy import BigInteger, Enum, Float, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.schemas.transaction_schema import TransactionType

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, unique=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    cash: Mapped[float] = mapped_column(Float, nullable=False)
    type : Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("category.id"), nullable=False, index=True)
    category = relationship("Category", back_populates="transactions")

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    user = relationship("User", back_populates="transactions")


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True,unique=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="categories")

    transactions = relationship("Transaction", back_populates="category", cascade="all, delete")