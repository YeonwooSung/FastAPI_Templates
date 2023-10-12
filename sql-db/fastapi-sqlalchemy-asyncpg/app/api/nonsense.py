from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.nonsense import Nonsense
from app.schemas.nnonsense import NonsenseResponse, NonsenseSchema

router = APIRouter(prefix="/v1/nonsense")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=NonsenseResponse)
async def create_nonsense(payload: NonsenseSchema, db_session: AsyncSession = Depends(get_db)):
    nonsense = Nonsense(**payload.model_dump())
    await nonsense.save(db_session)
    return nonsense


@router.get("/", response_model=NonsenseResponse)
async def find_nonsense(
    name: str,
    db_session: AsyncSession = Depends(get_db),
):
    return await Nonsense.find(db_session, name)


@router.delete("/")
async def delete_nonsense(name: str, db_session: AsyncSession = Depends(get_db)):
    nonsense = await Nonsense.find(db_session, name)
    return await nonsense.delete(nonsense, db_session)


@router.patch("/", response_model=NonsenseResponse)
async def update_nonsense(
    payload: NonsenseSchema,
    name: str,
    db_session: AsyncSession = Depends(get_db),
):
    nonsense = await Nonsense.find(db_session, name)
    await nonsense.update(db_session, **payload.model_dump())
    return nonsense


@router.post("/", response_model=NonsenseResponse)
async def merge_nonsense(
    payload: NonsenseSchema,
    db_session: AsyncSession = Depends(get_db),
):
    nonsense = Nonsense(**payload.model_dump())
    await nonsense.save_or_update(db_session)
    return nonsense
