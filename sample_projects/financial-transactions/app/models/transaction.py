import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# cusom modules
from app.db import Base


class TransactionType(str, enum.Enum):
    """트랜잭션 유형"""
    CREDIT = "CREDIT"  # 입금
    DEBIT = "DEBIT"    # 출금
    TRANSFER = "TRANSFER"  # 계좌 이체


class TransactionStatus(str, enum.Enum):
    """트랜잭션 상태"""
    PENDING = "PENDING"      # 대기 중
    PROCESSING = "PROCESSING"  # 처리 중
    COMPLETED = "COMPLETED"  # 완료
    FAILED = "FAILED"        # 실패


class Account(Base):
    """계좌 모델"""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True, index=True, nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    version = Column(Integer, default=1, nullable=False)  # 낙관적 락을 위한 버전
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 계좌와 관련된 트랜잭션
    transactions = relationship("Transaction", back_populates="account")

    # 버전과 계좌번호에 대한 복합 인덱스 생성
    __table_args__ = (
        Index('idx_account_version', 'account_number', 'version'),
    )


class Transaction(Base):
    """트랜잭션 모델"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    reference_id = Column(String, nullable=True)  # 연관 트랜잭션 ID (이체 등)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 관계 설정
    account = relationship("Account", back_populates="transactions")
