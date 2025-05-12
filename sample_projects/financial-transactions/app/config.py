import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # PostgreSQL 설정
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "transaction_db")
    DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # Redis 설정
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    
    # 락 설정
    LOCK_TIMEOUT: int = int(os.getenv("LOCK_TIMEOUT", "10"))  # 10초
    LOCK_RETRY_COUNT: int = int(os.getenv("LOCK_RETRY_COUNT", "5"))
    LOCK_RETRY_DELAY: float = float(os.getenv("LOCK_RETRY_DELAY", "0.2"))  # 0.2초

    class Config:
        env_file = ".env"

settings = Settings()
