import traceback
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from models import Teacher
from sqlalchemy import update
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from utils import DBConnector, Logger
from schema import TeacherSchema

router = APIRouter()
connector = DBConnector()
logger = Logger().get_logger()


@router.get("/", tags=["Teacher"])
def get_all_teachers(
    offset: int = 0, limit: int = 10, engine: Engine = Depends(connector.get_engine)
):
    """API to fetch info of all the teachers."""
    try:
        session = Session(engine)
        teachers = session.query(Teacher).offset(offset).limit(limit).all()
        session.close()

        return teachers
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to fetch list of teachers"
        )


@router.post("/", tags=["Teacher"])
def create_teacher(
    teacher: TeacherSchema, engine: Engine = Depends(connector.get_engine)
):
    """API to create a new teacher.

    Args:
        teacher (TeacherSchema): Teacher object to be created.

    Raises:
        HTTPException
    """
    try:
        if teacher.id == None:
            teacher.id = UUID(str(uuid4()))

        session = Session(engine)

        session.add(
            Teacher(
                id=str(teacher.id),
                name=teacher.name,
                department=teacher.department,
                subject=teacher.subject,
            )
        )
        session.commit()
        session.close()

        response = {
            "id": teacher.id,
            "message": f"Teacher {teacher.name} created successfully with ID {teacher.id}.",
        }

        return response
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create the teacher."
        )


@router.put("/{id}", tags=["Teacher"])
def update_teacher(
    id: str, teacher: TeacherSchema, engine: Engine = Depends(connector.get_engine)
):
    """API to update a teacher.

    Args:
        id (str): ID of the teacher to be updated
        teacher (TeacherSchema): Teacher object

    Raises:
        HTTPException
    """
    try:
        if teacher.id == None:
            teacher.id = UUID(str(uuid4()))

        session = Session(engine)

        session.execute(
            update(Teacher)
            .where(Teacher.id == id)
            .values(
                name=teacher.name,
                department=teacher.department,
                subject=teacher.subject,
            )
        )

        session.commit()
        session.close()

        response = {
            f"Teacher {teacher.name} updated successfully with ID {teacher.id}."
        }

        return response
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to update the teacher."
        )


@router.delete("/{id}", tags=["Teacher"])
def delete_teacher(id: str, engine: Engine = Depends(connector.get_engine)):
    """Deletes a Teacher from the database.

    Args:
        id (str): ID of the teacher to be deleted
    """
    try:
        session = Session(engine)

        session.delete(session.query(Teacher).filter(Teacher.id == id).first())
        session.commit()
        session.close()
        response = {f"Teacher with ID {id} deleted successfully."}

        return response
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to delete the teacher."
        )
