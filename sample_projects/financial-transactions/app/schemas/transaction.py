from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# custom modules
from app.models.transaction import TransactionType, TransactionStatus


# 계좌 스키마
class AccountBase(BaseModel):
    account_number: str

class AccountCreate(AccountBase):
    balance: float = 0.0


class AccountResponse(AccountBase):
    id: int
    balance: float
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 트랜잭션 스키마
class TransactionBase(BaseModel):
    amount: float
    type: TransactionType
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    account_number: str


class TransferCreate(BaseModel):
    from_account: str
    to_account: str
    amount: float
    description: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: int
    transaction_id: str
    account_id: int
    status: TransactionStatus
    reference_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 오류 응답 스키마
class ErrorResponse(BaseModel):
    detail: str
