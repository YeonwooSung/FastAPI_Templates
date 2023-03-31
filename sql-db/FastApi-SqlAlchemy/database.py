from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from settings  import settings

# SQLALCHEMY_DATABASE_URL = f'postgresql://{postgres}:{root}@{127.0.0.1}:{5432}/{db_fastapi}'
print("settings.database_username", settings.database_username)
print("settings.database_password", settings.database_password)
print("settings.database_hostname", settings.database_hostname)
print("settings.database_port", settings.database_port)
print("settings.database_name", settings.database_name)

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()