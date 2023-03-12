from dataclasses import Field
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid



class UserBase(BaseModel):
    id: int
    fname: str
    lname: str
    email: EmailStr
    password: str

    class Config:
        orm_mode = True