import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

# custom modules
from containers import Container
from middlewares import create_middlewares
from note.interface.controllers.note_controller import router as note_routers
from user.interface.controllers.user_controller import router as user_routers


app = FastAPI()
app.container = Container()

app.include_router(user_routers)
app.include_router(note_routers)

create_middlewares(app)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content=str(exc.errors()),
    )


@app.get("/")
def hello():
    return {"Hello": "FastAPI"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
