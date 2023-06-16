import traceback
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import update
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

# custom module
from fastapi_crud.utils.database import Database
from fastapi_crud.utils.logger import Logger
from fastapi_crud.api.models.user import User
from fastapi_crud.api.schema.user import UserSchema
from fastapi_crud.api.repository.user import UserRepository


# global variables
router = APIRouter()
connector = Database()
logger = Logger().get_logger()


@router.get("/", tags=["User"])
async def get_all_students(
    offset: int = 0,
    limit: int = 10,
    engine: Engine = Depends(connector.get_engine),
):
    """
    API to fetch info of all the users.

    Args:
        offset (int, optional): Offset. Defaults to 0.
        limit (int, optional): Limit. Defaults to 10.
        engine (Engine, optional): Database engine. Defaults to Depends(connector.get_engine).
    """
    try:
        session = Session(engine)
        user_repository = UserRepository(session)
        users = await user_repository.get(offset, limit)

        session.close()

        return users
    except Exception:
        logger.error(traceback.format_exc())
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to fetch list of users"
        )


@router.post("/", tags=["User"])
async def create_user(user: UserSchema):
    """API to create a new user.

    Args:
        user (UserSchema): User object to be created.

    Raises:
        HTTPException
    """
    try:
        if user.id == None:
            user.id = UUID(str(uuid4()))

        with connector.get_session() as session:
            user_repository = UserRepository(session)
            user = await user_repository.create(user)

        response = {
            "id": user.id,
            "message": f"User {user.name} created successfully with ID {user.id}.",
        }

        return response
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to create the user.")


@router.put("/{id}", tags=["User"])
async def update_student(
    id: str,
    user: UserSchema
):
    """
    API to update an user.

    Args:
        id (str): ID of the user to be updated.
        user (UserSchema): User object to be updated.

    Raises:
        HTTPException
    """
    try:
        if user.id == None:
            user.id = UUID(str(uuid4()))

        with connector.get_session() as session:
            user_repository = UserRepository(session)
            user = await user_repository.update(user)

        response = {
            f"User {user.name} updated successfully with ID {user.id}."
        }

        return response
    except:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to update the user."
        )


@router.delete("/{id}", tags=["Student"])
async def delete_student(id: str, engine: Engine = Depends(connector.get_engine)):
    """Deletes a Student from the database.

    Args:
        id (str): ID of the student to be deleted.
        engine (Engine, optional): Database engine. Defaults to Depends(connector.get_engine).
    """
    try:
        with connector.get_session() as session:
            user_repository = UserRepository(session)
            await user_repository.delete(id)
        response = {f"User with ID {id} deleted successfully."}

        return response
    except:
        logger.exception(traceback.format_exc())
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to delete the user.")
