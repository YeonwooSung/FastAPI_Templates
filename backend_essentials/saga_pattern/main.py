# FastAPI 기반 금융 트랜잭션 서비스 (SAGA 패턴)

# 필요한 라이브러리 설치
# pip install fastapi uvicorn sqlalchemy pydantic python-dotenv redis

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid
import datetime
import json
import logging
import os
from dotenv import load_dotenv
import redis

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()

# Redis 연결 설정 (SAGA 오케스트레이터로 사용)
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

# 데이터베이스 설정
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./financial_transactions.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI 앱 인스턴스 생성
app = FastAPI(title="금융 트랜잭션 서비스", description="SAGA 패턴을 이용한 금융 트랜잭션 서비스")

# 의존성 주입 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 트랜잭션 상태 열거형
class TransactionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"

# 트랜잭션 타입 열거형
class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"

# 서비스 열거형
class ServiceName(str, Enum):
    ACCOUNT = "account_service"
    PAYMENT = "payment_service"
    NOTIFICATION = "notification_service"
    AUDIT = "audit_service"

# 데이터베이스 모델 정의
class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True, index=True)
    owner_name = Column(String)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    transactions = relationship("Transaction", back_populates="account")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"))
    transaction_type = Column(String)
    amount = Column(Float)
    recipient_account = Column(String, nullable=True)  # 송금 시 수신자 계좌
    status = Column(String, default=TransactionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    account = relationship("Account", back_populates="transactions")
    steps = relationship("TransactionStep", back_populates="transaction")

class TransactionStep(Base):
    __tablename__ = "transaction_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, ForeignKey("transactions.transaction_id"))
    step_name = Column(String)
    service_name = Column(String)
    status = Column(String, default=TransactionStatus.PENDING)
    payload = Column(String)  # JSON 형태로 저장
    compensation_payload = Column(String, nullable=True)  # 보상 트랜잭션용 데이터
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    transaction = relationship("Transaction", back_populates="steps")

# 테이블 생성
Base.metadata.create_all(bind=engine)

# Pydantic 모델 정의
class AccountCreate(BaseModel):
    account_number: str
    owner_name: str
    initial_balance: float = 0.0

class AccountResponse(BaseModel):
    id: int
    account_number: str
    owner_name: str
    balance: float
    created_at: datetime.datetime
    
    class Config:
        orm_mode = True

class TransactionCreate(BaseModel):
    account_number: str
    transaction_type: TransactionType
    amount: float
    recipient_account: Optional[str] = None

class TransactionResponse(BaseModel):
    transaction_id: str
    account_number: str
    transaction_type: str
    amount: float
    recipient_account: Optional[str]
    status: str
    created_at: datetime.datetime
    
    class Config:
        orm_mode = True

class TransactionStepResponse(BaseModel):
    step_name: str
    service_name: str
    status: str
    created_at: datetime.datetime
    
    class Config:
        orm_mode = True

class TransactionDetailResponse(TransactionResponse):
    steps: List[TransactionStepResponse]

# SAGA 패턴 구현을 위한 서비스 클래스
class SagaOrchestrator:
    def __init__(self):
        self.transaction_steps = {
            TransactionType.DEPOSIT: [
                {"name": "validate_account", "service": ServiceName.ACCOUNT},
                {"name": "update_balance", "service": ServiceName.ACCOUNT},
                {"name": "record_transaction", "service": ServiceName.AUDIT},
                {"name": "send_notification", "service": ServiceName.NOTIFICATION}
            ],
            TransactionType.WITHDRAWAL: [
                {"name": "validate_account", "service": ServiceName.ACCOUNT},
                {"name": "check_balance", "service": ServiceName.ACCOUNT},
                {"name": "update_balance", "service": ServiceName.ACCOUNT},
                {"name": "record_transaction", "service": ServiceName.AUDIT},
                {"name": "send_notification", "service": ServiceName.NOTIFICATION}
            ],
            TransactionType.TRANSFER: [
                {"name": "validate_source_account", "service": ServiceName.ACCOUNT},
                {"name": "validate_target_account", "service": ServiceName.ACCOUNT},
                {"name": "check_source_balance", "service": ServiceName.ACCOUNT},
                {"name": "decrease_source_balance", "service": ServiceName.ACCOUNT},
                {"name": "increase_target_balance", "service": ServiceName.ACCOUNT},
                {"name": "record_transaction", "service": ServiceName.AUDIT},
                {"name": "process_payment", "service": ServiceName.PAYMENT},
                {"name": "send_notification", "service": ServiceName.NOTIFICATION}
            ]
        }
        
    def create_transaction_steps(self, db: Session, transaction_id: str, transaction_type: TransactionType, **kwargs):
        """트랜잭션 단계 생성"""
        steps = []
        
        for step in self.transaction_steps.get(transaction_type, []):
            transaction_step = TransactionStep(
                transaction_id=transaction_id,
                step_name=step["name"],
                service_name=step["service"],
                payload=json.dumps(kwargs),
                compensation_payload=json.dumps(kwargs) if transaction_type != TransactionType.DEPOSIT else None
            )
            db.add(transaction_step)
            steps.append(transaction_step)
            
        db.commit()
        return steps
    
    async def execute_saga(self, background_tasks: BackgroundTasks, db: Session, transaction_id: str):
        """SAGA 실행"""
        # 백그라운드 작업으로 트랜잭션 처리
        background_tasks.add_task(self._process_transaction, transaction_id)
        return {"message": f"트랜잭션 {transaction_id} 처리 시작됨"}
    
    async def _process_transaction(self, transaction_id: str):
        """트랜잭션 처리 로직"""
        with SessionLocal() as db:
            transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
            if not transaction:
                logger.error(f"트랜잭션 {transaction_id}를 찾을 수 없습니다.")
                return
            
            transaction.status = TransactionStatus.PROCESSING
            db.commit()
            
            # 트랜잭션 단계 수행
            steps = db.query(TransactionStep).filter(
                TransactionStep.transaction_id == transaction_id
            ).order_by(TransactionStep.id).all()
            
            for i, step in enumerate(steps):
                try:
                    # 단계 처리 시작
                    step.status = TransactionStatus.PROCESSING
                    db.commit()
                    
                    # 실제 서비스 호출 (여기서는 시뮬레이션)
                    await self._execute_step(db, step)
                    
                    # 단계 완료
                    step.status = TransactionStatus.COMPLETED
                    db.commit()
                except Exception as e:
                    logger.error(f"단계 {step.step_name} 실행 중 오류 발생: {str(e)}")
                    
                    # 단계 실패
                    step.status = TransactionStatus.FAILED
                    db.commit()
                    
                    # 보상 트랜잭션 실행
                    transaction.status = TransactionStatus.COMPENSATING
                    db.commit()
                    
                    await self._compensate_transaction(db, transaction_id, i)
                    return
            
            # 모든 단계가 성공적으로 완료됨
            transaction.status = TransactionStatus.COMPLETED
            db.commit()
            logger.info(f"트랜잭션 {transaction_id} 성공적으로 완료됨")
    
    async def _execute_step(self, db: Session, step: TransactionStep):
        """단계 실행 (실제 서비스 호출을 시뮬레이션)"""
        logger.info(f"단계 '{step.step_name}' 실행 중 (서비스: {step.service_name})")
        payload = json.loads(step.payload)
        
        if step.service_name == ServiceName.ACCOUNT:
            if step.step_name == "validate_account":
                account = db.query(Account).filter(
                    Account.account_number == payload.get("account_number")
                ).first()
                if not account:
                    raise ValueError(f"계좌번호 {payload.get('account_number')}가 존재하지 않습니다")
                
            elif step.step_name == "validate_target_account":
                target_account = db.query(Account).filter(
                    Account.account_number == payload.get("recipient_account")
                ).first()
                if not target_account:
                    raise ValueError(f"수신자 계좌번호 {payload.get('recipient_account')}가 존재하지 않습니다")
                
            elif step.step_name in ["check_balance", "check_source_balance"]:
                account = db.query(Account).filter(
                    Account.account_number == payload.get("account_number")
                ).first()
                if account.balance < payload.get("amount", 0):
                    raise ValueError(f"잔액 부족: 필요 금액 {payload.get('amount')}, 현재 잔액 {account.balance}")
                
            elif step.step_name == "update_balance":
                account = db.query(Account).filter(
                    Account.account_number == payload.get("account_number")
                ).first()
                if payload.get("transaction_type") == TransactionType.DEPOSIT:
                    account.balance += payload.get("amount", 0)
                elif payload.get("transaction_type") == TransactionType.WITHDRAWAL:
                    account.balance -= payload.get("amount", 0)
                db.commit()
                
            elif step.step_name == "decrease_source_balance":
                account = db.query(Account).filter(
                    Account.account_number == payload.get("account_number")
                ).first()
                account.balance -= payload.get("amount", 0)
                db.commit()
                
            elif step.step_name == "increase_target_balance":
                target_account = db.query(Account).filter(
                    Account.account_number == payload.get("recipient_account")
                ).first()
                target_account.balance += payload.get("amount", 0)
                db.commit()
        
        elif step.service_name == ServiceName.AUDIT:
            # 감사 로그 기록 (실제로는 별도 서비스로 구현)
            logger.info(f"감사 로그 기록: {payload}")
            
        elif step.service_name == ServiceName.PAYMENT:
            # 결제 처리 (실제로는 외부 API 호출)
            logger.info(f"결제 처리: {payload}")
            
        elif step.service_name == ServiceName.NOTIFICATION:
            # 알림 발송 (실제로는 메시징 서비스)
            logger.info(f"알림 발송: {payload}")
        
        # 단계 처리 시간 시뮬레이션 (실제 구현에서는 제거)
        import asyncio
        await asyncio.sleep(0.1)
    
    async def _compensate_transaction(self, db: Session, transaction_id: str, failed_step_index: int):
        """보상 트랜잭션 실행 (실패 시 롤백)"""
        logger.info(f"트랜잭션 {transaction_id}에 대한 보상 트랜잭션 실행 중")
        
        # 실패한 단계까지 역순으로 보상 트랜잭션 실행
        steps = db.query(TransactionStep).filter(
            TransactionStep.transaction_id == transaction_id
        ).order_by(TransactionStep.id.desc()).all()
        
        for step in steps:
            if step.id <= failed_step_index:
                continue  # 실패한 단계 이후의 단계는 이미 실행되지 않았으므로 보상 필요 없음
                
            try:
                # 보상 트랜잭션 실행
                step.status = TransactionStatus.COMPENSATING
                db.commit()
                
                await self._compensate_step(db, step)
                
                step.status = TransactionStatus.COMPENSATED
                db.commit()
            except Exception as e:
                logger.error(f"보상 트랜잭션 {step.step_name} 실행 중 오류: {str(e)}")
                step.status = TransactionStatus.FAILED
                db.commit()
        
        # 트랜잭션 상태 업데이트
        transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
        transaction.status = TransactionStatus.COMPENSATED
        db.commit()
        logger.info(f"트랜잭션 {transaction_id}에 대한 보상 트랜잭션 완료")
    
    async def _compensate_step(self, db: Session, step: TransactionStep):
        """단계 보상 로직 실행"""
        if not step.compensation_payload:
            logger.info(f"단계 {step.step_name}에 대한 보상 데이터가 없습니다")
            return
            
        logger.info(f"단계 '{step.step_name}'에 대한 보상 트랜잭션 실행 중")
        payload = json.loads(step.compensation_payload)
        
        if step.service_name == ServiceName.ACCOUNT:
            if step.step_name == "decrease_source_balance":
                # 출금 취소: 잔액 복구
                account = db.query(Account).filter(
                    Account.account_number == payload.get("account_number")
                ).first()
                account.balance += payload.get("amount", 0)
                db.commit()
                
            elif step.step_name == "increase_target_balance":
                # 입금 취소: 잔액 복구
                target_account = db.query(Account).filter(
                    Account.account_number == payload.get("recipient_account")
                ).first()
                target_account.balance -= payload.get("amount", 0)
                db.commit()
                
            elif step.step_name == "update_balance":
                # 잔액 업데이트 취소
                account = db.query(Account).filter(
                    Account.account_number == payload.get("account_number")
                ).first()
                if payload.get("transaction_type") == TransactionType.DEPOSIT:
                    account.balance -= payload.get("amount", 0)
                elif payload.get("transaction_type") == TransactionType.WITHDRAWAL:
                    account.balance += payload.get("amount", 0)
                db.commit()
        
        elif step.service_name == ServiceName.PAYMENT:
            # 결제 취소 로직
            logger.info(f"결제 취소: {payload}")
            
        elif step.service_name == ServiceName.NOTIFICATION:
            # 실패 알림 발송
            logger.info(f"트랜잭션 실패 알림 발송: {payload}")
        
        # 보상 처리 시간 시뮬레이션 (실제 구현에서는 제거)
        import asyncio
        await asyncio.sleep(0.1)

# API 라우트 정의
saga_orchestrator = SagaOrchestrator()

@app.post("/accounts/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    """새 계좌 생성"""
    # 기존 계좌 확인
    existing_account = db.query(Account).filter(Account.account_number == account.account_number).first()
    if existing_account:
        raise HTTPException(status_code=400, detail="이미 존재하는 계좌번호입니다")
    
    # 새 계좌 생성
    db_account = Account(
        account_number=account.account_number,
        owner_name=account.owner_name,
        balance=account.initial_balance
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    return db_account

@app.get("/accounts/{account_number}", response_model=AccountResponse)
def get_account(account_number: str, db: Session = Depends(get_db)):
    """계좌 정보 조회"""
    account = db.query(Account).filter(Account.account_number == account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail="계좌를 찾을 수 없습니다")
    return account

@app.post("/transactions/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    """새 트랜잭션 생성 및 SAGA 실행"""
    # 계좌 확인
    account = db.query(Account).filter(Account.account_number == transaction.account_number).first()
    if not account:
        raise HTTPException(status_code=404, detail="계좌를 찾을 수 없습니다")
    
    # 송금인 경우 수신자 계좌 필수
    if transaction.transaction_type == TransactionType.TRANSFER and not transaction.recipient_account:
        raise HTTPException(status_code=400, detail="송금 시 수신자 계좌번호가 필요합니다")
    
    # 트랜잭션 ID 생성
    transaction_id = str(uuid.uuid4())
    
    # 트랜잭션 기록
    db_transaction = Transaction(
        transaction_id=transaction_id,
        account_id=account.id,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        recipient_account=transaction.recipient_account,
        status=TransactionStatus.PENDING
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    # SAGA 단계 생성
    saga_orchestrator.create_transaction_steps(
        db,
        transaction_id,
        transaction.transaction_type,
        account_number=transaction.account_number,
        recipient_account=transaction.recipient_account,
        amount=transaction.amount,
        transaction_type=transaction.transaction_type
    )
    
    # SAGA 실행 (비동기)
    await saga_orchestrator.execute_saga(background_tasks, db, transaction_id)
    
    return {
        "transaction_id": db_transaction.transaction_id,
        "account_number": transaction.account_number,
        "transaction_type": db_transaction.transaction_type,
        "amount": db_transaction.amount,
        "recipient_account": db_transaction.recipient_account,
        "status": db_transaction.status,
        "created_at": db_transaction.created_at
    }

@app.get("/transactions/{transaction_id}", response_model=TransactionDetailResponse)
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """트랜잭션 상세 정보 조회"""
    transaction = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="트랜잭션을 찾을 수 없습니다")
    
    account = db.query(Account).filter(Account.id == transaction.account_id).first()
    steps = db.query(TransactionStep).filter(TransactionStep.transaction_id == transaction_id).all()

    return {
        "transaction_id": transaction.transaction_id,
        "account_number": account.account_number,
        "transaction_type": transaction.transaction_type,
        "amount": transaction.amount,
        "recipient_account": transaction.recipient_account,
        "status": transaction.status,
        "created_at": transaction.created_at,
        "steps": steps
    }

@app.get("/transactions/", response_model=List[TransactionResponse])
def list_transactions(account_number: Optional[str] = None, db: Session = Depends(get_db)):
    """트랜잭션 목록 조회"""
    query = db.query(Transaction)
    
    if account_number:
        account = db.query(Account).filter(Account.account_number == account_number).first()
        if not account:
            raise HTTPException(status_code=404, detail="계좌를 찾을 수 없습니다")
        query = query.filter(Transaction.account_id == account.id)
    
    transactions = query.order_by(Transaction.created_at.desc()).limit(100).all()
    
    result = []
    for transaction in transactions:
        account = db.query(Account).filter(Account.id == transaction.account_id).first()
        result.append({
            "transaction_id": transaction.transaction_id,
            "account_number": account.account_number,
            "transaction_type": transaction.transaction_type,
            "amount": transaction.amount,
            "recipient_account": transaction.recipient_account,
            "status": transaction.status,
            "created_at": transaction.created_at
        })
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
