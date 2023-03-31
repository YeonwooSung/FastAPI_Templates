from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Student(Base):
    """Student model representing a student table."""

    __tablename__ = "student"
    id = Column(UUID, primary_key=True)
    name = Column(String(50))
    department = Column(String(200))
    year = Column(Integer)

    def __repr__(self):
        return f"Student(id={self.id!r}, name={self.name!r}, department={self.fullname!r}, year={self.year})"
