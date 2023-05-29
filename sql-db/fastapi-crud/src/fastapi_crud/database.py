from sqlalchemy import create_engine

# custom module
from fastapi_crud.utils.logger import Logger

# init logger
logger = Logger().get_logger()


class Database:
    def __init__(self) -> None:
        self.engine = create_engine("mysql+mysqldb://scott:tiger@localhost/test")

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

database_instance = Database()
