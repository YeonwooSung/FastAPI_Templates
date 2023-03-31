import os

from sqlalchemy import create_engine

from .logger import Logger
from .singleton import Singleton

DSN_CONSTANT = "postgresql://{}:{}@{}"

logger = Logger().get_logger()


class DBConnector(metaclass=Singleton):
    """Create a singleton connection pool with the database.

    Args:
        metaclass (_type_, optional): _description_. Defaults to Singleton.
    """

    def __init__(self) -> None:
        """Initialize."""
        self.engine = None
        self.dsn = None
        user_name = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST")
        self.dsn = DSN_CONSTANT.format(user_name, password, host)

    def create_engine(self):
        """Create a connection pool with the database.

        Raises:
            ex: Ex
        """
        try:
            logger.debug("Creating a DB engine")
            if self.engine is None:
                self.engine = create_engine(self.dsn, pool_size=100, max_overflow=0)
        # TODO: Replace with more sophisticated exception handling
        except Exception as ex:
            logger.debug(f"Failed to create a DB engine, {str(ex)}")

    def get_engine(self):
        """Get the database engine.

        Returns:
            Engine: Database engine.
        """
        return self.engine

    def dispose_connection(self):
        """Close the Database connection pool."""
        self.engine.dispose(True)
