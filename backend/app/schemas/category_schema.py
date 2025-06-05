from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    title: str = Field(..., max_length=100)

class CategoryOut(CategoryBase):
    id: int
