from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"

class TransactionCreate(BaseModel):
    title: str = Field(..., max_length=100)
    cash: float = Field(..., ge=0)
    category_id: int = Field(..., ge=0)
    type: TransactionType

class TransactionUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    cash: Optional[float] = Field(None, ge=0)
    category_id: Optional[int] = Field(None, ge=0)
    type: TransactionType = Field(None)

class TransactionOut(BaseModel):
    id: int
    title: str
    cash: float
    type: TransactionType
    category_id: int = Field(..., ge=0)
    created_at: datetime

    class Config:
        from_attributes = True  # для Pydantic v2 вместо orm_mode