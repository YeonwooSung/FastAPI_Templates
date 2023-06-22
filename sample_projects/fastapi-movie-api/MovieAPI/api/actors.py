from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from MovieAPI.utils.db import get_session  # type: ignore
from MovieAPI.api.schemas.movie_actor_schema import Actor, ActorInput
from MovieAPI.api.schemas.user_schema import User
from MovieAPI.security.hashing import get_current_user


router = APIRouter(prefix="/api/actors")

@router.get("/{actor_id}")
def get_actor(
    actor_id: int,
    session: Session = Depends(get_session)
) -> Actor:
    '''
    Retrieve the details of a specific actor by their ID.

    Args:
        actor_id (int): Actor ID.
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Raises:
        HTTPException: If actor with given ID is not found.

    Returns:
        Actor: Actor details.
    '''
    actor: Actor | None = session.get(Actor, actor_id)
    if actor:
        return actor

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Actor with id={actor_id} not found"
    )


@router.get("/")
def get_actors(
    name: str | None = Query(None),
    birthdate: date | None = Query(None),
    nationality: str | None = Query(None),
    session: Session = Depends(get_session)
) -> list[Actor]:
    '''
    Retrieve a list of actors with optional filtering, sorting, and pagination.

    Args:
        actor_id (int): Actor ID.
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Returns:
        list[Actor]: List of actors.
    '''
    query = select(Actor)

    if name:
        query = query.where(Actor.last_name == name)
    if birthdate:
        query = query.where(Actor.date_of_birth == birthdate)
    if nationality:
        query = query.where(Actor.nationality == nationality)

    return session.exec(query).all()


@router.post("/", response_model=Actor, status_code=201)
def add_actor(
    actor_input: ActorInput,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Actor:
    '''
    Add a new actor to the database.

    Args:
        actor_input (ActorInput): Actor details.
        current_user (User, optional): Currently logged in user. Defaults to Depends(get_current_user).
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Returns:
        Actor: Newly created actor.
    '''
    new_actor: Actor = Actor.from_orm(actor_input)
    session.add(new_actor)
    session.commit()
    session.refresh(new_actor)
    return new_actor


@router.delete("/{actor_id}", status_code=204)
def delete_actor(
    actor_id: int,
    session: Session = Depends(get_session)
) -> None:
    '''
    Remove a specific actor from the database by their ID.

    Args:
        actor_id (int): Actor ID.
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Raises:
        HTTPException: If actor with given ID is not found.
    '''
    actor: Actor | None = session.get(Actor, actor_id)
    if actor:
        session.delete(actor)
        session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor with id={actor_id} not found"
        )


@router.put("/{actor_id}", response_model=Actor)
def update_actor(
    actor_id: int,
    new_actor: ActorInput,
    session: Session = Depends(get_session)
) -> Actor:
    '''
    Remove a specific actor from the database by their ID.

    Args:
        actor_id (int): Actor ID.
        new_actor (ActorInput): New actor details.
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Raises:
        HTTPException: If actor with given ID is not found.

    Returns:
        Actor: Updated actor details.
    '''
    actor: Actor | None = session.get(Actor, actor_id)
    if actor:
        for field, value in new_actor.dict().items():
            if value is not None:
                setattr(actor, field, value)
        session.commit()
        return actor
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor with id={actor_id} not found"
        )
