from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class UserSchema(BaseModel):
    """
    Represents a student model for the student API.

    Attributes:
        id (Optional[UUID]): Student ID.
        name (str): Student name.
        age (int): Student age.
    """

    id: Optional[UUID]
    name: str
    age: int

    class Config:
        orm_mode = True
