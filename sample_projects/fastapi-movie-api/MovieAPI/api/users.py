from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

# import custom modules
from MovieAPI.utils.db import get_session
from MovieAPI.api.schemas.user_schema import User, UserInput
from MovieAPI.security.hashing import get_password_hash


router = APIRouter(prefix="/api/users")


@router.get("/{user_id}")
def get_user(user_id: int, session: Session = Depends(get_session)) -> User:
    '''
    Retrieve the details of a specific user by their ID.

    Args:
        user_id (int): User ID.
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Raises:
        HTTPException: If user with given ID is not found.

    Returns:
        User: User details.
    '''
    user: User | None = session.get(User, user_id)
    if user:
        return user

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with id={user_id} not found"
    )


@router.get("/")
def get_users(
    email: str | None = Query(None),
    session: Session = Depends(get_session)
) -> list[User]:
    '''
    Retrieve a list of users.

    Args:
        email (str, optional): Filter users by email. Defaults to None.
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Returns:
        list[User]: List of users.
    '''
    query = select(User)

    if email:
        query = query.where(User.email == email)

    return session.exec(query).all()


@router.post("/", response_model=User, status_code=201)
def add_user(user_input: UserInput, session: Session = Depends(get_session)) -> User:
    '''
    Register a new user in the system.

    Args:
        user_input (UserInput): User details.
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Returns:
        User: User details.
    '''
    hashed_password = get_password_hash(user_input.password)
    user_input.password = hashed_password

    new_user: User = User.from_orm(user_input)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, session: Session = Depends(get_session)) -> None:
    '''
    Remove a specific user from the database by their ID.

    Args:
        user_id (int): User ID.
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Raises:
        HTTPException: If user with given ID is not found.
    '''
    user: User | None = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found"
        )


@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    new_user: UserInput,
    session: Session = Depends(get_session)
) -> User:
    '''
    Update the details of a specific user by their ID.

    Args:
        user_id (int): User ID.
        new_user (UserInput): New user details.
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Raises:
        HTTPException: If user with given ID is not found.

    Returns:
        User: Updated user details.
    '''
    user: User | None = session.get(User, user_id)
    if user:
        for field, value in new_user.dict().items():
            if value is not None:
                setattr(user, field, value)
        session.commit()
        return user
    else:
        raise HTTPException(status_code=404, detail=f"User with id={user_id} not found")
