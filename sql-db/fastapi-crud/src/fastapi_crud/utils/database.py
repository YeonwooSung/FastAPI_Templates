from sqlalchemy import create_engine
import os
from typing import Union

# custom module
from fastapi_crud.utils.singleton import Singleton
from fastapi_crud.utils.logger import Logger

# constant for database connection template string
DSN_CONSTANT = "postgresql://{}:{}@{}"
# init logger
logger = Logger().get_logger()

# define isolation levels
_ISOLATION_LEVELS = ["AUTOCOMMIT", "READ COMMITTED", "READ UNCOMMITTED", "REPEATABLE READ", "SERIALIZABLE"]


class Database(metaclass=Singleton):
    '''
    Create a singleton connection pool with the database.
    '''
    def __init__(self) -> None:
        self.engine = None
        user_name = os.getenv("DB_USER", 'postgres')
        password = os.getenv("DB_PASSWORD", 'postgres')
        host = os.getenv("DB_HOST", 'localhost')
        self.dsn = DSN_CONSTANT.format(user_name, password, host)

    def create_engine(
        self,
        pool_size:int=10,
        max_overflow:int=0,
        isolation_level:str="REPEATABLE READ"
    ) -> None:
        """Create a connection pool with the database.

        Args:
            pool_size (int, optional): [description]. Defaults to 10.
            max_overflow (int, optional): [description]. Defaults to 0.
        """
        try:
            if isolation_level not in _ISOLATION_LEVELS:
                raise ValueError(f"Isolation level {isolation_level} is not supported. Supported levels are {_ISOLATION_LEVELS}")

            logger.debug(f"Creating a DB engine ({self.dsn}) with pool_size={pool_size} and max_overflow={max_overflow} :: isolation_level={isolation_level}")
            if self.engine is None:
                self.engine = create_engine(self.dsn, pool_size=pool_size, max_overflow=max_overflow, isolation_level=isolation_level)
        # TODO: Replace with more sophisticated exception handling
        except Exception as ex:
            logger.error(f"Failed to create a DB engine, {str(ex)}")

    def get_engine(self):
        """Get the database engine.

        Returns:
            Engine: Database engine.
        """
        if self.engine is None:
            self.create_engine()
        return self.engine

    def dispose_connection(self):
        """Close the Database connection pool."""
        self.engine.dispose(True)
