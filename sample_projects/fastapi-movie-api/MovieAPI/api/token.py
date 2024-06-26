from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

# import custom modules
from MovieAPI.utils.db import get_session
from MovieAPI.api.schemas.token_schema import Token
from MovieAPI.api.schemas.user_schema import User
from MovieAPI.security.hashing import create_access_token, verify_password


ACCESS_TOKEN_EXPIRE_MINUTES = 3000000

router = APIRouter(prefix="/api")


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
):
    '''
    Authenticate a user and generate an access token.

    Args:
        form_data (Annotated[OAuth2PasswordRequestForm, Depends()]): OAuth2 password request form.
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Raises:
        HTTPException: 401 exception if user is not found or password is incorrect.

    Returns:
        Token: Access token.
    '''
    query = select(User).where(User.email == form_data.username)
    user: User | None = session.exec(query).first()

    if user is None:
        raise_401_exception()

    assert user is not None

    if not verify_password(form_data.password, user.password):
        raise_401_exception()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


def raise_401_exception():
    '''
    Raise 401 exception.

    Raises:
        HTTPException: 401 exception.
    '''
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
