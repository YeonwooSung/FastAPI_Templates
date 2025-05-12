from typing import List
from fastapi import APIRouter, HTTPException, BackgroundTasks

# custom modules
from app.schemas.transaction import (
    AccountCreate, AccountResponse, 
    TransactionCreate, TransactionResponse,
    TransferCreate,
)
from app.services.transaction_service import (
    OptimisticLockError, 
    LockAcquisitionError, 
    InsufficientFundsError,
    AccountNotFoundError
)
from app.dependencies import TransactionServiceDep, DatabaseDep


router = APIRouter(prefix="/api/v1", tags=["transactions"])


@router.post("/accounts", response_model=AccountResponse, status_code=201)
async def create_account(
    account_data: AccountCreate, 
    service: TransactionServiceDep,
    db: DatabaseDep,
):
    """새 계좌 생성 API"""
    try:
        return await service.create_account(db, account_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/accounts/{account_number}", response_model=AccountResponse)
async def get_account(
    account_number: str, 
    service: TransactionServiceDep,
    db: DatabaseDep,
):
    """계좌 조회 API"""
    account = await service.get_account(db, account_number)
    if not account:
        raise HTTPException(status_code=404, detail=f"Account {account_number} not found")
    return account


@router.post("/transactions", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    transaction_data: TransactionCreate,
    background_tasks: BackgroundTasks,
    service: TransactionServiceDep,
    db: DatabaseDep,
):
    """트랜잭션 생성 및 처리 API"""
    try:
        # 트랜잭션 생성
        transaction = await service.create_transaction(db, transaction_data)

        # 백그라운드에서 트랜잭션 처리
        background_tasks.add_task(
            service.process_transaction,
            db=db,
            transaction_id=transaction.transaction_id
        )

        return transaction
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/transfers", response_model=List[TransactionResponse], status_code=201)
async def transfer(
    transfer_data: TransferCreate,
    service: TransactionServiceDep,
    db: DatabaseDep,
):
    """계좌 이체 API"""
    try:
        # 이체 트랜잭션 생성 및 처리
        debit_tx, credit_tx = await service.transfer(db, transfer_data)

        return [debit_tx, credit_tx]
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InsufficientFundsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except (OptimisticLockError, LockAcquisitionError) as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
