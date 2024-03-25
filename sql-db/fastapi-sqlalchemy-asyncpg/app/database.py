from collections.abc import AsyncGenerator

from sqlalchemy.event import listens_for
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# custom modules
from app.config import settings as global_settings
from app.utils.logging import AppLogger

logger = AppLogger.__call__().get_logger()

engine = create_async_engine(
    global_settings.asyncpg_url.unicode_string(),
    future=True,
    echo=True,
)

# expire_on_commit=False will prevent attributes from being expired
# after commit.
AsyncSessionFactory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False,)


# Dependency
async def get_db() -> AsyncGenerator:
    async with AsyncSessionFactory() as session:
        # logger.debug(f"ASYNC Pool: {engine.pool.status()}")
        yield session


# add event listener to listen for new connections
@listens_for(engine, "connect")
def my_on_connect(dbapi_con, connection_record):
    print("New DBAPI connection:", dbapi_con)
