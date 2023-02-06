from typing import List

from pydantic import BaseModel


class Item(BaseModel):
    id: int
    title: str
    owner_id: int
    description: str = None

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    email: str
    is_active: bool

    class Config:
        orm_mode = True


class UserWithItems(BaseModel):
    id: int
    email: str
    is_active: bool
    items: List[Item] = [] # this could lead to N+1

    class Config:
        orm_mode = True
