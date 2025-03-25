# FastAPI based financial transaction service (with SAGA pattern)

## Instructions

```bash
# install
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv redis

# run
uvicorn main:app --reload
```

## SAGA Pattern Implementation

- Each transaction is divided into multiple steps for processing
- Automatically executes compensating transactions in case of failure to maintain consistency

## Key Features

- Account creation and retrieval
- Support for Deposit, Withdrawal, and Transfer transactions
- Transaction status tracking and step-by-step progress monitoring

## Components

- SagaOrchestrator: Manages transaction steps and orchestration
- Account Service: Account validation, balance inquiry/modification
- Payment Service: Actual payment processing (simulated)
- Notification Service: User notifications (simulated)
- Audit Service: Transaction recording (simulated)

## Technologies Used

- FastAPI: REST API implementation
- SQLAlchemy: ORM
- Redis: For SAGA orchestration state management (currently code-only)
- Background Tasks: Asynchronous transaction processing
