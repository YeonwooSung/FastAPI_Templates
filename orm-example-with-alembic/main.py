from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI

from middlewares import RequestID, RequestLogger
from routers import student, teacher
from utils import DBConnector

app = FastAPI(title="FastAPI Boilerplate", openapi_url="/openapi")

API_PREFIX = "/v1"

load_dotenv()
connector = DBConnector()


@app.on_event("startup")
def startup_event():
    """Performs the actions required at the startup of the application."""
    connector.create_engine()


@app.on_event("shutdown")
def shutdown_event():
    """Performs the actions required at the application shutdown."""
    connector.dispose_connection()


# Add middlewares
app.add_middleware(RequestLogger)
app.add_middleware(RequestID)


# Add routers
app.include_router(student.router, prefix=API_PREFIX + "/student")
app.include_router(teacher.router, prefix=API_PREFIX + "/teacher")
