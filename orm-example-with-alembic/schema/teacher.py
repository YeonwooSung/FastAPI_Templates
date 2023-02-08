from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TeacherSchema(BaseModel):
    """Represents a teacher model for the teacher API."""

    id: Optional[UUID]
    name: str
    department: str
    subject: int

    class Config:
        orm_mode = True
