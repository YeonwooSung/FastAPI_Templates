from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.stuff import Stuff
from app.schemas.stuff import StuffResponse, StuffSchema
from app.utils.logging import AppLogger

logger = AppLogger.__call__().get_logger()

router = APIRouter(prefix="/v1/stuff")


@router.post("/add_many", status_code=status.HTTP_201_CREATED)
async def create_multi_stuff(payload: list[StuffSchema], db_session: AsyncSession = Depends(get_db)):
    try:
        stuff_instances = [Stuff(**stuff.model_dump()) for stuff in payload]
        db_session.add_all(stuff_instances)
        await db_session.commit()
    except SQLAlchemyError as ex:
        # logger.exception(ex)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=repr(ex)) from ex
    else:
        logger.info(f"{len(stuff_instances)} instances of Stuff inserted into database.")
        return True


@router.post("", status_code=status.HTTP_201_CREATED, response_model=StuffResponse)
async def create_stuff(payload: StuffSchema, db_session: AsyncSession = Depends(get_db)):
    stuff = Stuff(**payload.model_dump())
    await stuff.save(db_session)
    return stuff


@router.get("/{name}", response_model=StuffResponse)
async def find_stuff(
    name: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await Stuff.find(db_session, name)


@router.delete("/{name}")
async def delete_stuff(name: str, db_session: AsyncSession = Depends(get_db)):
    stuff = await Stuff.find(db_session, name)
    return await Stuff.delete(stuff, db_session)


@router.patch("/{name}", response_model=StuffResponse)
async def update_stuff(
    payload: StuffSchema,
    name: str,
    db_session: AsyncSession = Depends(get_db),
):
    stuff = await Stuff.find(db_session, name)
    await stuff.update(db_session, **payload.model_dump())
    return stuff
