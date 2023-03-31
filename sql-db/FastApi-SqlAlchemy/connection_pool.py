import asyncpg

# from psycopg2 import pool
from settings import settings


class Database:
    '''
    This class is used to create a connection pool to the database.

    Attributes:
        user: The username of the database.
        password: The password of the database.
        host: The host of the database.
        port: The port of the database.
        database: The name of the database.
        _connection_pool: The connection pool to the database.
        _cursor: The cursor to the database.
        con: The connection to the database.
    '''

    def __init__(self) -> None:
        '''
        The constructor for Database class.
        '''
        self.user = settings.database_username
        self.password = settings.database_password
        self.host = settings.database_hostname
        self.port = "5432"
        self.database = settings.database_name
        self._cursor = None

        self._connection_pool = None
        self.con = None


    async def connect(self) -> None:
        '''
        This method is used to create a connection pool to the database.
        If the connection pool is already created, it will do nothing.
        '''
        if not self._connection_pool:
            try:
                self._connection_pool = await asyncpg.create_pool(
                    min_size=1,
                    max_size=10,
                    command_timeout=60,
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                )

            except Exception as e:
                print(e)


    async def fetch_rows(self, query: str) -> list:
        '''
        This method is used to fetch rows from the database.

        Args:
            query: The query to be executed.

        Returns:
            The rows fetched from the database.
        '''
        if not self._connection_pool:
            await self.connect()
        else:
            self.con = await self._connection_pool.acquire()
            try:
                result = await self.con.fetch(query)
                print("Results", result)
                return result
            except Exception as e:
                print(e)
            finally:
                await self._connection_pool.release(self.con)


    async def execute(self, query: str):
        '''
        This method is used to execute a query on the database.

        Args:
            query: The query to be executed.

        Returns:
            The result of the query.
        '''
        if not self._connection_pool:
            await self.connect()
        else:
            self.con = await self._connection_pool.acquire()
            try:
                result = await self.con.execute(query)
                print("Results", result)
                return result
            except Exception as e:
                print(e)
            finally:
                await self._connection_pool.release(self.con)


# Create a database instance as a singleton.
database_instance = Database()
