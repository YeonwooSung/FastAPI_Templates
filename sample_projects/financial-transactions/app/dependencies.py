from fastapi import Depends
from typing import Annotated
from sqlalchemy.orm import Session

# custom modules
from app.db import get_db
from app.services.transaction_service import TransactionService
# from app.services.lock_service import DistributedLock


def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    """트랜잭션 서비스 의존성 주입"""
    service = TransactionService()
    service.initialize(db)
    return service


# 타입 힌트를 위한 의존성
TransactionServiceDep = Annotated[TransactionService, Depends(get_transaction_service)]
DatabaseDep = Annotated[Session, Depends(get_db)]
