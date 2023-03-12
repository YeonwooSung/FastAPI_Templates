from typing import Optional
from pydantic import BaseSettings

# This is a pydantic model for the enviroment variables


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str

    class Config:
        env_file = ".env"


settings = Settings()
