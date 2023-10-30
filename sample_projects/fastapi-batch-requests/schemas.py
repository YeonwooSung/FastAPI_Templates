from typing import Optional
from pydantic import BaseModel


class ProductBase(BaseModel):
    title: str
    description: Optional[str]


class ProductUpsert(ProductBase):
    ...


class Product(ProductBase):
    id: int
