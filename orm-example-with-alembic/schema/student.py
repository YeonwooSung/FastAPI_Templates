from pydantic import BaseModel
from uuid import UUID, uuid4
from typing import Optional

class StudentSchema(BaseModel):
    """Represents a student model for the student API."""

    id: Optional[UUID]
    name: str
    department: str
    year: int

    class Config:
        orm_mode = True