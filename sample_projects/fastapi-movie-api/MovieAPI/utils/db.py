import os
from typing import Any, Generator

from sqlmodel import Session, create_engine


is_testing = os.environ.get("TESTING")

if is_testing:
    database_url = "sqlite:///./tests/mydb/movieapi.db"
else:
    database_url = "sqlite:///./MovieAPI/mydb/movieapi.db"


engine = create_engine(
    database_url,
    echo=True,
    connect_args={"check_same_thread": False})


def get_session() -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session
