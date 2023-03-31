from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Teacher(Base):
    """Teacher model representing a student table."""

    __tablename__ = "teacher"
    id = Column(UUID, primary_key=True)
    name = Column(String(50))
    department = Column(String(200))
    subject = Column(Integer)  # subject code

    def __repr__(self):
        return f"Student(id={self.id!r}, name={self.name!r}, department={self.fullname!r}, subject={self.subject})"
