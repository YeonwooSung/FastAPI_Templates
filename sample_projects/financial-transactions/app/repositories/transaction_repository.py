from typing import Optional, List
from sqlalchemy.orm import Session

# custom modules
from app.models.transaction import Transaction, TransactionStatus
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    """트랜잭션 리포지토리"""

    def __init__(self, db: Session):
        super().__init__(db, Transaction)

    def get_by_transaction_id(self, transaction_id: str) -> Optional[Transaction]:
        """트랜잭션 ID로 조회"""
        return self.db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id
        ).first()


    def get_by_account_id(self, account_id: int) -> List[Transaction]:
        """계좌 ID로 트랜잭션 목록 조회"""
        return self.db.query(Transaction).filter(
            Transaction.account_id == account_id
        ).all()


    def update_status(self, transaction_id: str, status: TransactionStatus) -> bool:
        """트랜잭션 상태 업데이트"""
        result = self.db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id
        ).update({"status": status})

        return result > 0
