from random import randint
from sqlalchemy.orm import Session
from sqlalchemy import update
from uuid import uuid4

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

    async def bulk_insert(self, users: list[User]) -> list[User]:
        '''
        Bulk insert users.

        Args:
            users (list[User]): List of users to be inserted.

        Returns:
            list[User]: List of inserted users.
        '''
        self.db.bulk_save_objects(users)
        self.db.commit()
        return users

    async def bulk_insert_mapping(self, num:int=2000) -> list[User]:
        '''
        Bulk insert users using mapping.

        Args:
            num (int, optional): Number of users to be inserted. Defaults to 2000.

        Returns:
            list[User]: List of inserted users.
        '''
        self.db.bulk_insert_mappings(
            User,
            [
                {"id": str(uuid4()), "name": "user_" + str(i), "age": randint(1, 100)}
                for i in range(num)
            ],
        )
        self.db.commit()

    async def insert_or_update(self, user: User) -> User:
        '''
        Insert or update a user.

        Args:
            user (User): User object to be inserted or updated.

        Returns:
            User: Inserted or updated user object.
        '''
        self.db.merge(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    async def bulk_update(self, users: list[User]) -> list[User]:
        '''
        Bulk update users.

        Args:
            users (list[User]): List of users to be updated.

        Returns:
            list[User]: List of updated users.
        '''
        self.db.bulk_update_mappings(User, users)
        self.db.commit()
        return users
