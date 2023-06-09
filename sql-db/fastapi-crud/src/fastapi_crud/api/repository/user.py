from sqlalchemy.orm import Session
from sqlalchemy import update

# custom module
from fastapi_crud.api.models.user import User

class UserRepository:
    '''User Repository'''

    def __init__(self, db: Session):
        self.db = db

    async def get(self, offset: int = 0, limit: int = 10) -> list[User]:
        '''
        Get all users.

        Args:
            offset (int, optional): Offset. Defaults to 0.
            limit (int, optional): Limit. Defaults to 10.

        Returns:
            list[User]: List of users.
        '''
        return self.db.query(User).offset(offset).limit(limit).all()

    async def create(self, user: User) -> User:
        '''
        Create a new user

        Args:
            user (User): User object to be created.

        Returns:
            User: Created user object.
        '''
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    async def update(self, user: User) -> User:
        '''
        Update an existing user.

        Args:
            user (User): User object to be updated.

        Returns:
            User: Updated user object.
        '''
        # self.db.commit()
        self.db.execute(
            update(User)
            .where(User.id == user.id)
            .values(name=user.name, age=user.age)
        )
        self.db.commit()
        self.db.refresh(user)
        return user

    async def delete(self, id: str) -> User:
        '''
        Delete an existing user.

        Args:
            id (str): User id to be deleted.

        Returns:
            User: Deleted user object.
        '''
        self.db.delete(self.db.query(User).filter(User.id == id).first())
        self.db.commit()
