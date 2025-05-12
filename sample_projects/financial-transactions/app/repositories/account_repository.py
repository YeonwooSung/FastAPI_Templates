from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

# custom modules
from app.models.transaction import Account
from app.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    """계좌 리포지토리"""
    
    def __init__(self, db: Session):
        super().__init__(db, Account)
    
    def get_by_account_number(self, account_number: str) -> Optional[Account]:
        """계좌번호로 조회"""
        return self.db.query(Account).filter(
            Account.account_number == account_number
        ).first()


    def update_balance_with_version(
        self, 
        account_id: int, 
        new_balance: float, 
        expected_version: int
    ) -> bool:
        """버전 확인 후 잔액 업데이트 (Compare-and-Set)"""
        from datetime import datetime
        
        result = self.db.query(Account).filter(
            and_(
                Account.id == account_id,
                Account.version == expected_version
            )
        ).update({
            "balance": new_balance,
            "version": expected_version + 1,
            "updated_at": datetime.now()
        })
        
        return result > 0
