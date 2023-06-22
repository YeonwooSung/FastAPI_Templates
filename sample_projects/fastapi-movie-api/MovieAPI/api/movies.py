from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

# import custom modules
from MovieAPI.utils.db import get_session
from MovieAPI.api.schemas.movie_actor_schema import Actor, Movie
from MovieAPI.api.schemas.movie_actor_schema import MovieActorLink, MovieInput


router = APIRouter(prefix="/api/movies")

@router.get("/")
def get_movies(
    release_year: int | None = None,
    session: Session = Depends(get_session)
) -> list[Movie]:
    '''
    Retrieve a list of movies with optional filtering, sorting, and pagination.

    Args:
        release_year (int, optional): Filter movies by release year. Defaults to None.
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Returns:
        list[Movie]: List of movies.
    '''
    query = select(Movie)
    if release_year:
        query = query.where(Movie.release_year == release_year)
    return session.exec(query).all()


@router.get("/{movie_id}")
def get_movie(
    movie_id: int,
    session: Session = Depends(get_session)
) -> Movie:
    '''
    Retrieve the details of a specific movie by its ID.

    Args:
        movie_id (int): Movie ID.
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Raises:
        HTTPException: If movie with given ID is not found.

    Returns:
        Movie: Movie details.
    '''
    movie: Movie | None = session.get(Movie, movie_id)
    if movie:
        return movie

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Movie with id={movie_id} not found"
    )


@router.post("/", response_model=Movie, status_code=201)
def add_movie(
    movie_input: MovieInput,
    session: Session = Depends(get_session)
) -> Movie:
    '''
    Add a new movie to the database.

    Args:
        movie_input (MovieInput): Movie details.
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Returns:
        Movie: Movie details.
    '''
    new_movie: Movie = Movie.from_orm(movie_input)
    session.add(new_movie)
    session.commit()
    session.refresh(new_movie)
    return new_movie


@router.delete("/{movie_id}", status_code=204)
def delete_movie(
    movie_id: int,
    session: Session = Depends(get_session)
) -> None:
    '''
    Remove a specific movie from the database by its ID.

    Args:
        movie_id (int): Movie ID.
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Raises:
        HTTPException: If movie with given ID is not found.
    '''
    movie: Movie | None = session.get(Movie, movie_id)
    if movie:
        session.delete(movie)
        session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id={movie_id} not found"
        )


@router.put("/{movie_id}", response_model=Movie)
def update_movie(
    movie_id: int,
    new_movie: MovieInput,
    session: Session = Depends(get_session)
) -> Movie:
    '''
    Update the details of a specific movie by its ID.

    Args:
        movie_id (int): Movie ID.
        new_movie (MovieInput): New movie details.
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Raises:
        HTTPException: If movie with given ID is not found.

    Returns:
        Movie: Updated movie details.
    '''
    movie: Movie | None = session.get(Movie, movie_id)
    if movie:
        # update movie from database with values from new_movie
        for field, value in new_movie.dict().items():
            if value is not None:
                setattr(movie, field, value)
        session.commit()
        return movie
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id={movie_id} not found"
        )


@router.post("/{movie_id}/actors/{actor_id}", status_code=204)
def add_actor_to_movie(
    movie_id: int,
    actor_id: int,
    session: Session = Depends(get_session)
) -> None:
    '''
    Add an actor to a movie.

    Args:
        movie_id (int): Movie ID.
        actor_id (int): Actor ID.
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Raises:
        HTTPException: If movie or actor with given ID is not found.
    '''
    movie: Movie | None = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id={movie_id} not found"
        )

    actor: Actor | None = session.get(Actor, actor_id)
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor with id={actor_id} not found"
        )

    link = MovieActorLink(movie_id=movie_id, actor_id=actor_id)
    session.add(link)
    session.commit()


@router.delete("/{movie_id}/actors/{actor_id}", status_code=204)
def remove_actor_from_movie(
    movie_id: int,
    actor_id: int,
    session: Session = Depends(get_session)
) -> None:
    '''
    Remove an actor from a movie.

    Args:
        movie_id (int): Movie ID.
        actor_id (int): Actor ID.
        session (Session, optional): Database session. Defaults to Depends(get_session).

    Raises:
        HTTPException: If movie, actor or link between them is not found.
    '''
    movie: Movie | None = session.get(Movie, movie_id)
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with id={movie_id} not found"
        )

    actor: Actor | None = session.get(Actor, actor_id)
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor with id={actor_id} not found"
        )

    link: MovieActorLink | None = session.get(MovieActorLink, (movie_id, actor_id))
    if not link:
        raise HTTPException(
            status_code=404,
            detail=f"Actor {actor_id} not associated with movie {movie_id}"
        )

    session.delete(link)
    session.commit()
