import uuid
import logging
from datetime import datetime
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

# custom modules
from app.models.transaction import Account, Transaction, TransactionType, TransactionStatus
from app.schemas.transaction import AccountCreate, TransactionCreate, TransferCreate
from app.services.lock_service import DistributedLock, LockAcquisitionError
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository


logger = logging.getLogger(__name__)


class OptimisticLockError(Exception):
    """낙관적 락 충돌 예외"""
    pass

class InsufficientFundsError(Exception):
    """잔액 부족 예외"""
    pass


class AccountNotFoundError(Exception):
    """계좌 없음 예외"""
    pass


class TransactionService:
    """금융 트랜잭션 서비스"""

    def __init__(self):
        self.account_repo = None
        self.transaction_repo = None

    def initialize(self, db: Session):
        """리포지토리 초기화"""
        self.account_repo = AccountRepository(db)
        self.transaction_repo = TransactionRepository(db)

    async def create_account(self, db: Session, account_data: AccountCreate) -> Account:
        """
        새 계좌 생성을 위한 서비스.
        계좌번호의 unique 제약조건 확인을 위해 IntegrityError 예외 처리.
        만약 동일 계좌번호에 대해 중복 생성 요청 시, Rollback 후 ValueError 발생.
        """
        # 데이터 준비
        account = Account(
            account_number=account_data.account_number,
            balance=account_data.balance,
            version=1
        )

        # DB에 저장
        db.add(account)
        try:
            db.commit()
            db.refresh(account)
            return account
        except IntegrityError:
            db.rollback()
            raise ValueError(f"Account number {account_data.account_number} already exists")


    async def get_account(self, db: Session, account_number: str) -> Optional[Account]:
        """계좌 조회"""
        return db.query(Account).filter(Account.account_number == account_number).first()


    async def create_transaction(
        self, 
        db: Session, 
        transaction_data: TransactionCreate
    ) -> Transaction:
        """새 트랜잭션 생성 (상태: PENDING)"""
        # 계좌 확인
        account = await self.get_account(db, transaction_data.account_number)
        if not account:
            raise AccountNotFoundError(f"Account {transaction_data.account_number} not found")

        # 트랜잭션 생성
        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            account_id=account.id,
            amount=transaction_data.amount,
            type=transaction_data.type,
            status=TransactionStatus.PENDING,
            description=transaction_data.description
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction


    async def process_transaction(
        self, 
        db: Session, 
        transaction_id: str,
        max_retries: int = 3
    ) -> Transaction:
        """
        트랜잭션 처리 함수
        Compare-and-Set 알고리즘과 분산락 결합
        """
        # 트랜잭션 조회
        transaction = db.query(Transaction).filter(
            Transaction.transaction_id == transaction_id
        ).first()

        if not transaction:
            raise ValueError(f"Transaction {transaction_id} not found")

        if transaction.status != TransactionStatus.PENDING:
            logger.info(f"Transaction {transaction_id} already processed with status {transaction.status}")
            return transaction

        # 계좌 조회
        account = db.query(Account).filter(Account.id == transaction.account_id).first()
        if not account:
            raise AccountNotFoundError(f"Account {transaction.account_id} not found")

        # 분산락 획득 시도
        resource_key = f"account:{account.account_number}"

        try:
            async with DistributedLock(resource_key):
                # 트랜잭션 처리 중 상태로 변경
                transaction.status = TransactionStatus.PROCESSING
                db.commit()

                retries = 0
                while retries < max_retries:
                    try:
                        # 현재 계좌 상태 다시 조회 (낙관적 락을 위해)
                        db.refresh(account)
                        current_version = account.version
                        current_balance = account.balance

                        # 트랜잭션 유형에 따른 잔액 계산
                        new_balance = current_balance
                        if transaction.type == TransactionType.CREDIT:
                            new_balance += transaction.amount
                        elif transaction.type == TransactionType.DEBIT:
                            if current_balance < transaction.amount:
                                transaction.status = TransactionStatus.FAILED
                                db.commit()
                                raise InsufficientFundsError(
                                    f"Insufficient funds: {current_balance} < {transaction.amount}"
                                )
                            new_balance -= transaction.amount

                        # Compare-and-Set 업데이트: 버전이 일치할 때만 업데이트
                        result = db.query(Account).filter(
                            and_(
                                Account.id == account.id,
                                Account.version == current_version
                            )
                        ).update({
                            "balance": new_balance,
                            "version": current_version + 1,
                            "updated_at": datetime.now()
                        })

                        if result == 0:
                            # 버전 불일치 (다른 프로세스가 동시에 수정)
                            retries += 1
                            logger.warning(
                                f"Optimistic lock conflict for account {account.account_number}, "
                                f"retry {retries}/{max_retries}"
                            )
                            continue

                        # 트랜잭션 완료 처리
                        transaction.status = TransactionStatus.COMPLETED
                        db.commit()
                        db.refresh(transaction)
                        return transaction

                    except IntegrityError:
                        db.rollback()
                        retries += 1

                # 최대 재시도 횟수 초과
                transaction.status = TransactionStatus.FAILED
                db.commit()
                raise OptimisticLockError(
                    f"Failed to process transaction after {max_retries} retries"
                )

        except LockAcquisitionError:
            # 락 획득 실패
            transaction.status = TransactionStatus.FAILED
            db.commit()
            raise

        finally:
            db.close()


    async def transfer(
        self, 
        db: Session, 
        transfer_data: TransferCreate,
        max_retries: int = 3
    ) -> Tuple[Transaction, Transaction]:
        """
        계좌 이체 처리
        출금 및 입금 트랜잭션을 하나의 작업으로 처리
        """
        # 양쪽 계좌 확인
        from_account = await self.get_account(db, transfer_data.from_account)
        to_account = await self.get_account(db, transfer_data.to_account)

        if not from_account:
            raise AccountNotFoundError(f"Source account {transfer_data.from_account} not found")
        if not to_account:
            raise AccountNotFoundError(f"Destination account {transfer_data.to_account} not found")

        # 참조 ID 생성
        transfer_ref = str(uuid.uuid4())

        # 출금 트랜잭션 생성
        debit_tx = Transaction(
            transaction_id=str(uuid.uuid4()),
            account_id=from_account.id,
            amount=transfer_data.amount,
            type=TransactionType.DEBIT,
            status=TransactionStatus.PENDING,
            reference_id=transfer_ref,
            description=transfer_data.description or "Transfer out"
        )

        # 입금 트랜잭션 생성
        credit_tx = Transaction(
            transaction_id=str(uuid.uuid4()),
            account_id=to_account.id,
            amount=transfer_data.amount,
            type=TransactionType.CREDIT,
            status=TransactionStatus.PENDING,
            reference_id=transfer_ref,
            description=transfer_data.description or "Transfer in"
        )

        db.add(debit_tx)
        db.add(credit_tx)
        db.commit()
        db.refresh(debit_tx)
        db.refresh(credit_tx)

        # 두 계좌의 분산락 획득 (데드락 방지를 위해 항상 계좌번호 순으로 락 획득)
        account_keys = sorted([from_account.account_number, to_account.account_number])

        try:
            # 첫 번째 계좌 락 획득
            async with DistributedLock(f"account:{account_keys[0]}"):
                # 두 번째 계좌 락 획득
                async with DistributedLock(f"account:{account_keys[1]}"):
                    # 출금 처리
                    debit_result = await self.process_transaction(db, debit_tx.transaction_id, max_retries)
                    
                    # 출금 성공 시 입금 처리
                    if debit_result.status == TransactionStatus.COMPLETED:
                        credit_result = await self.process_transaction(db, credit_tx.transaction_id, max_retries)
                        return debit_result, credit_result
                    else:
                        # 출금 실패 시 입금도 실패 처리
                        credit_tx.status = TransactionStatus.FAILED
                        db.commit()
                        return debit_result, credit_tx

        except (LockAcquisitionError, OptimisticLockError, InsufficientFundsError) as e:
            # 락 획득 실패 또는 기타 오류 시 두 트랜잭션 모두 실패 처리
            if debit_tx.status != TransactionStatus.FAILED:
                debit_tx.status = TransactionStatus.FAILED

            credit_tx.status = TransactionStatus.FAILED
            db.commit()
            raise e
