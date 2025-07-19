from pydantic_settings import BaseSettings


# Configuration
class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/ingestion_db"
    db_pool_min_size: int = 5
    db_pool_max_size: int = 20
    
    # Batch processing
    batch_size: int = 1000
    batch_timeout_seconds: int = 30
    max_batch_memory_mb: int = 100
    
    # Redis for batch coordination
    redis_url: str = "redis://localhost:6379"
    
    # API
    api_title: str = "Batch Ingestion API"
    api_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"


settings = Settings()
