import traceback
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from models import Student
from schema import StudentSchema
from sqlalchemy import update
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from utils import DBConnector, Logger

router = APIRouter()
connector = DBConnector()
logger = Logger().get_logger()


@router.get("/", tags=["Student"])
def get_all_students(
    offset: int = 0, limit: int = 10, engine: Engine = Depends(connector.get_engine)
):
    """API to fetch info of all the students."""
    try:
        session = Session(engine)
        students = session.query(Student).offset(offset).limit(limit).all()
        session.close()

        return students
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to fetch list of students"
        )


@router.post("/", tags=["Student"])
def create_student(
    student: StudentSchema, engine: Engine = Depends(connector.get_engine)
):
    """API to create a new student.

    Args:
        student (StudentSchema): Student object to be created.

    Raises:
        HTTPException
    """
    try:
        if student.id == None:
            student.id = UUID(str(uuid4()))

        session = Session(engine)

        session.add(
            Student(
                id=str(student.id),
                name=student.name,
                department=student.department,
                year=student.year,
            )
        )
        session.commit()

        session.close()

        response = {
            "id": student.id,
            "message": f"Student {student.name} created successfully with ID {student.id}.",
        }

        return response
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create the student."
        )


@router.put("/{id}", tags=["Student"])
def update_student(
    id: str, student: StudentSchema, engine: Engine = Depends(connector.get_engine)
):
    """API to update a student.

    Args:
        id (str): ID of the student to be updated
        student (StudentSchema): Student object

    Raises:
        HTTPException
    """
    try:
        if student.id == None:
            student.id = UUID(str(uuid4()))

        session = Session(engine)

        session.execute(
            update(Student)
            .where(Student.id == id)
            .values(name=student.name, department=student.department, year=student.year)
        )

        session.commit()
        session.close()

        response = {
            f"Student {student.name} updated successfully with ID {student.id}."
        }

        return response
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to update the student."
        )


@router.delete("/{id}", tags=["Student"])
def delete_student(id: str, engine: Engine = Depends(connector.get_engine)):
    """Deletes a Student from the database.

    Args:
        id (str): ID of the student to be deleted
    """
    try:
        session = Session(engine)

        session.delete(session.query(Student).filter(Student.id == id).first())
        session.commit()
        session.close()
        response = {f"Student with ID {id} deleted successfully."}

        return response
    except Exception as ex:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to delete the student."
        )
