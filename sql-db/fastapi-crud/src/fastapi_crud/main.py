from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# configure base dir
import sys
sys.path.append('.')
sys.path.append('..')

# custom module
from fastapi_crud.utils.database import Database
from fastapi_crud.middleware.request_id import RequestID
from fastapi_crud.middleware.request_logger import RequestLogger
from fastapi_crud.api.user import router as user_router


# Fast API
app = FastAPI()

origins = ["*"]
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# add custom middlewares
app.add_middleware(RequestLogger)
app.add_middleware(RequestID)

# create a singleton instance of Database
database_instance = Database()

# Start up event
@app.on_event("startup")
async def startup():
    database_instance.create_engine()

@app.get("/")
async def root():
    return {"message": "CMMS APP"}

# include API routers
app.include_router(user_router, prefix="/user")

#TODO 1) Complex schema & N+1 problem preventing codes
#TODO 2) sqlalchemy repository & Fake repository
#TODO 3) Unit test codes
