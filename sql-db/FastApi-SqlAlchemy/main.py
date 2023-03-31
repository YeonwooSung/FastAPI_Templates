from fastapi import FastAPI
from routers.user import view as userview
from database import engine
from connection_pool import database_instance
from fastapi.middleware.cors import CORSMiddleware

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

# Including routers
app.include_router(userview.router)

# Start up event
@app.on_event("startup")
async def startup():
    await database_instance.connect()

# Main route
@app.get("/")
async def root():
    return {"message": "CMMS APP"}
