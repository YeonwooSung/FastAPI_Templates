from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class User(Base):
    """User model representing an user table."""

    __tablename__ = "user"

    id = Column(UUID, primary_key=True)
    name = Column(String(50))
    age = Column(Integer)

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, age={self.age})"
