import asyncpg

# from psycopg2 import pool
from settings import settings


class Database:
    def __init__(self):
        self.user = settings.database_username
        self.password = settings.database_password
        self.host = settings.database_hostname
        self.port = "5432"
        self.database = settings.database_name
        self._cursor = None

        self._connection_pool = None
        self.con = None

    async def connect(self):
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

    async def fetch_rows(self, query: str):
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
                
database_instance = Database()