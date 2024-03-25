import uuid
from datetime import datetime
from typing import Any

import bcrypt
from passlib.context import CryptContext
from sqlalchemy import LargeBinary, String, event, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    _password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    @property
    def password(self):
        return self._password.decode("utf-8")

    @password.setter
    def password(self, password: str):
        self._password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password: str):
        return pwd_context.verify(password, self.password)

    @classmethod
    async def find(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()



# add event listener to listen for "insert"
@event.listens_for(User, "before_insert")
def user_before_insert(mapper, connection, target):
    # add new audit log
    table = UserAuditLog.__table__
    connection.execute(
        table.insert().values(
            user_id=target.id,
            action="insert",
            created_at=str(datetime.now())
        ),
        created_at=str(datetime.now())
    )


# new class for audit log
class UserAuditLog(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False)

    @classmethod
    async def find(cls, database_session: AsyncSession, where_conditions: list[Any]):
        _stmt = select(cls).where(*where_conditions)
        _result = await database_session.execute(_stmt)
        return _result.scalars().first()
