from unittest.mock import Mock
from app.services.transaction_service import TransactionService
from app.schemas.transaction import AccountCreate


def test_create_account():
    # Mock dependencies
    # mock_db = Mock()
    mock_account_repo = Mock()
    
    # Service setup
    service = TransactionService()
    service.account_repo = mock_account_repo

    # Test data
    account_data = AccountCreate(account_number="123456", balance=1000.0)

    # Execute
    result = service.create_account(account_data)

    # Assertions
    mock_account_repo.create.assert_called_once()
    assert result is not None
