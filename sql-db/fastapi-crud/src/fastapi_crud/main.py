from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# custom module
from fastapi_crud.utils.database import Database


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

# create a singleton instance of Database
database_instance = Database()

# Start up event
@app.on_event("startup")
async def startup():
    database_instance.create_engine()

@app.get("/")
async def root():
    return {"message": "CMMS APP"}
